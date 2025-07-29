import asyncio
import json
import re
from functools import cache
from os import environ
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Union,
    cast,
)

import aiohttp
from bs4 import BeautifulSoup
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool, tool
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from loguru import logger
from pydantic import BaseModel, Field
from rongda_mcp_server.api import ReportType, comprehensive_search, download_report_html
from rongda_mcp_server.models import FinancialReport

from xxy.chunker import TextChunker
from xxy.client import get_llm, get_slm
from xxy.config import load_config
from xxy.rongda_session import get_rongda_seesion
from xxy.stream import send_reasoning
from xxy.types import RongdaDoc

# Global chunker instance for tool usage
_document_chunker: Optional[TextChunker] = None


class AgentState(TypedDict):
    """Unified state for both document search and analysis"""

    user_question: str
    doc_id: str
    messages: List[Union[HumanMessage, AIMessage, ToolMessage]]

    # Search phase state
    found_documents: List[RongdaDoc]
    selected_doc_id: str

    # Analysis phase state
    document_loaded: bool
    final_answer: str


@tool
def load_document(text: str, chunk_size: int = 1000, overlap: int = 100) -> str:
    """
    Load a document into the text chunker for searching and reading.

    Args:
        text: The document text to load and chunk
        chunk_size: Size of each chunk in characters (default: 1000)
        overlap: Number of overlapping characters between chunks (default: 100)

    Returns:
        Status message with chunk count
    """
    global _document_chunker
    _document_chunker = TextChunker(text, chunk_size, overlap)
    chunk_count = _document_chunker.get_chunk_count()
    return f"Document loaded successfully. Created {chunk_count} chunks."


@tool
def answer(response: str) -> str:
    """
    Provide the final answer to the user's question.

    Args:
        response: The comprehensive answer to the user's question

    Returns:
        Confirmation that the answer was provided
    """
    return (
        f"Answer provided: {response[:100]}..."
        if len(response) > 100
        else f"Answer provided: {response}"
    )


async def get_rongda_doc(doc_id: str) -> str:
    session = await get_rongda_seesion()
    report = await download_report_html(
        session,
        FinancialReport(
            title="",
            content="",
            dateStr="",
            security_code="",
            downpath="",
            htmlpath=doc_id,
        ),
    )

    if report is not None:
        return report.content
    else:
        raise Exception(f"Failed to download report: {doc_id}")


async def load_document_node(state: AgentState) -> AgentState:
    """
    Node to load the document using the doc_id
    """
    doc_id = state["doc_id"]
    logger.info(f"📄 Loading document: {doc_id}")

    try:
        # Get the document content
        doc_content = await get_rongda_doc(doc_id)
        logger.info(
            f"📄 Document content loaded, length: {len(doc_content)} characters"
        )

        # Load it into the chunker
        result = load_document.func(doc_content)  # type: ignore[attr-defined]
        logger.debug(f"📄 Document chunked successfully: {result}")

        # Update state
        state["document_loaded"] = True
        state["messages"].append(
            AIMessage(content=f"Document {doc_id} loaded successfully. {result}")
        )

    except Exception as e:
        logger.exception(f"❌ Failed to load document {doc_id}")
        state["document_loaded"] = False
        state["messages"].append(
            AIMessage(content=f"Failed to load document {doc_id}: {str(e)}")
        )

    return state


@tool
def search_document(keywords: str, case_sensitive: bool = False) -> str:
    """
    Search for chunks in the loaded document containing specified keywords.

    Args:
        keywords: Keywords to search for (can be multiple words separated by spaces)
        case_sensitive: Whether search should be case sensitive (default: False)

    Returns:
        Search results with chunk indices and previews
    """
    if _document_chunker is None:
        return "No document loaded. Please load a document first using load_document."

    send_reasoning(f"Searching {keywords}")
    # Split keywords by spaces if multiple keywords provided
    keyword_list = keywords.split() if " " in keywords else [keywords]

    matching_indices = _document_chunker.search(keyword_list, case_sensitive)

    if not matching_indices:
        return f"No chunks found containing keywords: {keywords}"

    results = [f"Found {len(matching_indices)} chunks containing '{keywords}':"]

    logger.info(f"🔍 Found {len(matching_indices)} chunks containing '{keywords}'")

    for idx in matching_indices:
        chunk_info = _document_chunker.get_chunk_info(idx)
        results.append(f"- Chunk {idx}: {chunk_info['preview']}")

    return "\n".join(results)


@tool
def get_chunk(index: int) -> str:
    """
    Retrieve the full content of a specific chunk by its index.

    Args:
        index: The index of the chunk to retrieve

    Returns:
        The full content of the chunk at the specified index
    """
    if _document_chunker is None:
        return "No document loaded. Please load a document first using load_document."

    logger.info(f"🔍 Getting chunk {index}")
    try:
        chunk = _document_chunker.retrieval(index)
        chunk_info = _document_chunker.get_chunk_info(index)

        nav_info = []
        if chunk_info["has_previous"]:
            nav_info.append(f"Previous chunk: {index - 1}")
        if chunk_info["has_next"]:
            nav_info.append(f"Next chunk: {index + 1}")

        nav_text = f" ({', '.join(nav_info)})" if nav_info else ""

        return f"Chunk {index}{nav_text}:\n\n{chunk}"

    except IndexError as e:
        return str(e)


@tool
def get_next_chunk(current_index: int) -> str:
    """
    Get the next chunk after the specified index.

    Args:
        current_index: The current chunk index

    Returns:
        The content of the next chunk, or error message if not available
    """
    if _document_chunker is None:
        return "No document loaded. Please load a document first using load_document."

    next_index = current_index + 1

    logger.info(f"🔍 Getting next chunk {current_index}")

    try:
        chunk = _document_chunker.retrieval(next_index)
        chunk_info = _document_chunker.get_chunk_info(next_index)

        nav_info = []
        if chunk_info["has_previous"]:
            nav_info.append(f"Previous chunk: {next_index - 1}")
        if chunk_info["has_next"]:
            nav_info.append(f"Next chunk: {next_index + 1}")

        nav_text = f" ({', '.join(nav_info)})" if nav_info else ""

        return f"Chunk {next_index}{nav_text}:\n\n{chunk}"

    except IndexError:
        return (
            f"No next chunk available. Current chunk {current_index} is the last chunk."
        )


@tool
def get_previous_chunk(current_index: int) -> str:
    """
    Get the previous chunk before the specified index.

    Args:
        current_index: The current chunk index

    Returns:
        The content of the previous chunk, or error message if not available
    """
    if _document_chunker is None:
        return "No document loaded. Please load a document first using load_document."

    prev_index = current_index - 1
    logger.info(f"🔍 Getting previous chunk {current_index}")

    if prev_index < 0:
        return f"No previous chunk available. Current chunk {current_index} is the first chunk."

    try:
        chunk = _document_chunker.retrieval(prev_index)
        chunk_info = _document_chunker.get_chunk_info(prev_index)

        nav_info = []
        if chunk_info["has_previous"]:
            nav_info.append(f"Previous chunk: {prev_index - 1}")
        if chunk_info["has_next"]:
            nav_info.append(f"Next chunk: {prev_index + 1}")

        nav_text = f" ({', '.join(nav_info)})" if nav_info else ""

        return f"Chunk {prev_index}{nav_text}:\n\n{chunk}"

    except IndexError as e:
        return str(e)


@tool
def get_document_info() -> str:
    """
    Get information about the currently loaded document.

    Returns:
        Document statistics and overview
    """
    if _document_chunker is None:
        return "No document loaded. Please load a document first using load_document."
    logger.info(f"🔍 Getting document info")
    chunk_count = _document_chunker.get_chunk_count()
    total_length = len(_document_chunker.text)
    avg_chunk_size = total_length // chunk_count if chunk_count > 0 else 0

    return f"""Document Information:
- Total chunks: {chunk_count}
- Total text length: {total_length:,} characters
- Average chunk size: {avg_chunk_size} characters
- Chunk size setting: {_document_chunker.chunk_size}
- Overlap setting: {_document_chunker.overlap}
- Index range: 0 to {chunk_count - 1}"""


# Tool list for easy access
document_tools = [
    load_document,
    search_document,
    get_chunk,
    get_next_chunk,
    get_previous_chunk,
    get_document_info,
]


def should_continue(state: AgentState) -> str:
    """
    Determine whether to continue the agent loop or end
    """
    logger.trace("🔄 Evaluating whether to continue agent workflow...")

    # If document failed to load, end
    if not state["document_loaded"]:
        logger.trace("❌ Document not loaded - ending workflow")
        return "end"

    # If we have a final answer, end
    if state.get("final_answer"):
        logger.trace("✅ Final answer available - ending workflow")
        return "end"

    # Check the last message to see if it's an answer tool call
    last_message = state["messages"][-1] if state["messages"] else None
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "answer":
                logger.trace("✅ Answer tool called - ending workflow")
                return "end"

    # Continue the agent loop
    logger.trace("🔄 Continuing agent workflow...")
    return "continue"


def create_document_agent() -> CompiledStateGraph:
    """
    Create the document reading agent with LangGraph
    """
    # Get the LLM
    llm = get_llm()

    # All tools including the answer tool
    all_tools = document_tools + [answer]

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(all_tools)

    # Create system prompt
    system_prompt = """You are a document analysis agent. Your job is to:

1. Search through the loaded document to find relevant information
2. Read specific chunks that contain relevant information
3. Navigate between chunks to gather comprehensive context
4. Provide a thorough answer to the user's question

Available tools:
- search_document: Find chunks containing keywords
- get_chunk: Read full content of a specific chunk
- get_next_chunk/get_previous_chunk: Navigate between chunks
- get_document_info: Get document overview
- answer: Provide your final answer (call this when you have enough information)

Strategy:
1. Start by searching for keywords related to the user's question
2. Due to the length of document, you may find lots of related place, if so, refine your search keywords to narrow the scope
3. Read the relevant chunks found in search results
4. Due to the doc is from OCR, table may be split to a few tables, read the around section to avoid missing lines
5. If needed, read adjacent chunks for more context
6. Gather comprehensive information before answering
7. Call the 'answer' tool with your complete response

Be thorough and make sure you have sufficient information before providing an answer."""

    async def agent_node(state: AgentState) -> AgentState:
        """
        Main agent node that processes messages and calls tools
        """
        logger.trace("🤖 Agent called - processing messages and making decisions")

        messages: List[BaseMessage] = [SystemMessage(content=system_prompt)]
        messages.extend(state["messages"])

        # Add the user question as the latest human message if not already present
        if not any(
            isinstance(msg, HumanMessage) and state["user_question"] in msg.content
            for msg in messages
        ):
            messages.append(
                HumanMessage(
                    content=f"Please answer this question about the document: {state['user_question']}"
                )
            )
            logger.trace(f"❓ User question added: {state['user_question']}")

        # Get LLM response
        logger.debug("🧠 Calling LLM for reasoning...")
        response = await llm_with_tools.ainvoke(messages)
        logger.info(
            f"🧠 LLM response received with {len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0} tool calls"
        )

        # Update state with the response
        if isinstance(response, (HumanMessage, AIMessage, ToolMessage)):
            state["messages"].append(response)

        # If there are tool calls, execute them
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.trace(f"🔧 Executing {len(response.tool_calls)} tool calls")
            for i, tool_call in enumerate(response.tool_calls, 1):
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                logger.debug(
                    f"🔧 Tool {i}/{len(response.tool_calls)}: {tool_name} with args: {tool_args}"
                )

                # Find and execute the tool
                tool_func = None
                for tool in all_tools:
                    if tool.name == tool_name:
                        # For async tools, the function might be in 'coroutine' attribute instead of 'func'
                        tool_func = getattr(tool, "func", None) or getattr(
                            tool, "coroutine", None
                        )
                        break

                if tool_func:
                    try:
                        logger.trace(f"⚡ Executing tool: {tool_name}")
                        # Check if tool is async
                        if asyncio.iscoroutinefunction(tool_func):
                            tool_result = await tool_func(**tool_args)
                        else:
                            tool_result = tool_func(**tool_args)

                        # Special handling for answer tool
                        if tool_name == "answer":
                            state["final_answer"] = tool_args.get("response", "")
                            logger.debug(
                                f"✅ Final answer provided: {tool_args.get('response', '')[:100]}..."
                            )

                        logger.debug(
                            f"✅ Tool {tool_name} executed successfully: {tool_result[:100]}..."
                        )

                        # Add tool result to messages
                        state["messages"].append(
                            ToolMessage(
                                content=tool_result, tool_call_id=tool_call["id"]
                            )
                        )
                    except Exception as e:
                        logger.exception(f"❌ Error executing tool {tool_name}")
                        state["messages"].append(
                            ToolMessage(
                                content=f"Error executing {tool_name}: {str(e)}",
                                tool_call_id=tool_call["id"],
                            )
                        )
                else:
                    logger.error(f"❌ Tool not found: {tool_name}")
        else:
            logger.info("💭 No tool calls in LLM response - continuing reasoning")

        logger.trace("🤖 Agent node completed")
        return state

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("load_document", load_document_node)
    workflow.add_node("agent", agent_node)

    # Add edges
    workflow.set_entry_point("load_document")
    workflow.add_conditional_edges(
        "load_document", should_continue, {"continue": "agent", "end": END}
    )
    workflow.add_conditional_edges(
        "agent", should_continue, {"continue": "agent", "end": END}
    )

    return workflow.compile()
