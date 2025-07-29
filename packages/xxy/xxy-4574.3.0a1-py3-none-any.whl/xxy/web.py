import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from loguru import logger

from xxy.rongda_agent import process_document_question
from xxy.stream import (
    generate_stream_response,
    setup_streaming_queue,
)

logger.configure(extra={"request_id": "", "model_id": ""})  # Default values

app = FastAPI(
    title="XXY API",
    description="Document Q&A API for financial reports",
    version="1.0.0"
)

# Mount static files
app.mount("/chatbot", StaticFiles(directory="xxy/chatbot"), name="chatbot")

# Get API key from environment variable
API_KEY = os.getenv("XXY_API_KEY")
if not API_KEY:
    raise ValueError("XXY_API_KEY environment variable is not set")

# Model registry to store available models
MODELS = {
    "rongda": {
        "id": "rongda",
        "object": "model",
        "created": 1677652288,
        "owned_by": "xxy",
        "permission": [],
        "root": "rongda",
        "parent": None,
        "description": "Document Q&A model for financial reports",
    }
}


# Pydantic models for request/response validation
class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    stream: bool = Field(default=False, description="Whether to stream the response")
    company_code: Optional[str] = Field(default=None, description="Company code for document search")


class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]


class ModelInfo(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    permission: List[str]
    root: str
    parent: Optional[str]
    description: str


class ModelsListResponse(BaseModel):
    object: str
    data: List[ModelInfo]


class ErrorResponse(BaseModel):
    error: str


# Dependency for API key authentication
async def verify_api_key(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="No API key provided")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    api_key = authorization.split(" ")[1]
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


def parse_messages(message: Message) -> Union[AIMessage, HumanMessage]:
    if message.role == "user":
        return HumanMessage(content=message.content)
    elif message.role == "assistant":
        return AIMessage(content=message.content)
    else:
        raise ValueError(f"Unsupported message role: {message.role}")


def extract_messages_from_history(
    messages: List[Message],
) -> List[Union[AIMessage, HumanMessage]]:
    """Extract messages from the chat history in OpenAI format."""
    return [
        parse_messages(msg)
        for msg in messages[:-1]
        if msg.role in ["user", "assistant"]
    ]


async def process_with_model(
    model_id: str,
    user_question: str,
    request_body: Dict[str, Any],
    messages: List[Union[AIMessage, HumanMessage, ToolMessage]],
    request_id: str = "",
) -> str:
    """Process the request based on the model type."""
    if not request_id:
        logger.warning("No request ID provided, using a random one")
        request_id = str(uuid.uuid4())

    with logger.contextualize(request_id=request_id, model_id=model_id):
        logger.info('Processing request "{user_question}"', user_question=user_question)
        if model_id == "rongda":
            # Extract company_code from the request body
            company_code = request_body.get("company_code", "")

            return await process_document_question(
                user_question=user_question,
                company_code=company_code.split(",") if company_code else [],
                messages=messages,
            )
        else:
            raise ValueError(f"Unsupported model: {model_id}")


@app.get("/v1/models", response_model=ModelsListResponse)
async def list_models():
    """List available models."""
    return ModelsListResponse(
        object="list",
        data=[ModelInfo(**model_data) for model_data in MODELS.values()]
    )


@app.get("/v1/models/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str):
    """Get specific model information."""
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return ModelInfo(**MODELS[model_id])


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key),
    x_request_id: Optional[str] = Header(None, alias="x-request-id")
):
    """Handle chat completion requests with streaming support."""
    try:
        request_id = x_request_id or str(uuid.uuid4())

        # Validate model
        if request.model not in MODELS:
            raise HTTPException(status_code=400, detail=f"Model '{request.model}' not found")

        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Get the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        user_question = user_messages[-1].content

        if request.stream:
            # Set up streaming queue
            setup_streaming_queue()

            async def create_stream():
                # Start the processing task
                processing_task = asyncio.create_task(
                    process_with_model(
                        model_id=request.model,
                        user_question=user_question,
                        request_body=request.dict(),
                        messages=extract_messages_from_history(request.messages),
                        request_id=request_id,
                    )
                )

                # Generate streaming response
                async for chunk in generate_stream_response(processing_task):
                    yield chunk

            return StreamingResponse(
                create_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming response
            response = await process_with_model(
                model_id=request.model,
                user_question=user_question,
                request_body=request.dict(),
                messages=extract_messages_from_history(request.messages),
                request_id=request_id,
            )

            # Format response in OpenAI style
            return ChatCompletionResponse(
                id="chatcmpl-123",
                object="chat.completion",
                created=1677652288,
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        index=0,
                        message=Message(role="assistant", content=response),
                        finish_reason="stop"
                    )
                ]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and return proper JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions and return proper JSON responses."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
