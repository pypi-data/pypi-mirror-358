import asyncio
import json
import queue
from contextvars import ContextVar
from typing import Any, AsyncGenerator, Awaitable, Callable, Generator, Optional

# Context variables for streaming reasoning
reasoning_queue_var: ContextVar[Optional[asyncio.Queue[str]]] = ContextVar(
    "reasoning_queue", default=None
)


def setup_streaming_queue() -> asyncio.Queue[str]:
    """
    Set up a new streaming queue and set it in the context variable.
    Returns the created queue.
    """
    reasoning_queue = asyncio.Queue[str]()
    reasoning_queue_var.set(reasoning_queue)
    return reasoning_queue


def cleanup_streaming_queue() -> None:
    """
    Clean up the streaming queue from the context variable.
    """
    reasoning_queue_var.set(None)


def get_streaming_queue() -> Optional[asyncio.Queue[str]]:
    """
    Get the current streaming queue from context variable.
    """
    return reasoning_queue_var.get()


async def wait_streaming_queue(timeout: float = 0.1) -> str:
    """
    Wait for reasoning text from the streaming queue with timeout.
    """
    q = reasoning_queue_var.get()
    if q is None:
        raise RuntimeError("No streaming queue available")

    reasoning_text = await asyncio.wait_for(q.get(), timeout=timeout)
    return reasoning_text + "\n\n"


def send_reasoning(reasoning_text: str) -> None:
    """
    Send reasoning text to the streaming queue if available.
    This function can be called from anywhere in the codebase to stream reasoning.
    """
    q = reasoning_queue_var.get()
    if q and not q.full():
        try:
            # Put the reasoning text in the queue
            q.put_nowait(reasoning_text)
        except asyncio.QueueFull:
            # Queue is full, skip this reasoning chunk
            pass


def create_reasoning_chunk(
    reasoning_text: str, finish_reason: Optional[str] = None
) -> str:
    """
    Create a streaming chunk for reasoning data in OpenAI format.
    """
    chunk_data = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": 1677652288,
        "model": "rongda",
        "choices": [
            {
                "index": 0,
                "delta": {"reasoning": reasoning_text},
                "finish_reason": finish_reason,
            }
        ],
    }
    return f"data: {json.dumps(chunk_data)}\n\n"


def create_final_chunk(content: str) -> str:
    """
    Create the final chunk with the actual response content.
    """
    chunk_data = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": 1677652288,
        "model": "rongda",
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }
    return f"data: {json.dumps(chunk_data)}\n\n"


def create_done_chunk() -> str:
    """
    Create the final done chunk.
    """
    return "data: [DONE]\n\n"


async def generate_stream_response(
    processing_task: asyncio.Task[str], timeout: float = 0.1
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response chunks while processing task runs.

    Args:
        processing_task: The async task that processes the request
        timeout: Timeout for waiting for reasoning chunks

    Yields:
        Streaming chunks as strings
    """
    try:
        # Stream reasoning chunks while processing
        while True:
            try:
                # Wait for reasoning data with timeout
                reasoning_text = await wait_streaming_queue(timeout)
                yield create_reasoning_chunk(reasoning_text)
            except asyncio.TimeoutError:
                # Check if processing is done
                if processing_task.done():
                    break
                continue

        # Get the final response
        response = await processing_task

        # Send the final content chunk
        yield create_final_chunk(response)

        # Send done chunk
        yield create_done_chunk()

    except Exception as e:
        # Send error as reasoning chunk
        error_chunk = create_reasoning_chunk(f"Error: {str(e)}", "error")
        yield error_chunk
        yield create_done_chunk()
    finally:
        # Clean up
        cleanup_streaming_queue()


def create_sync_generator(
    async_gen: AsyncGenerator[str, None],
) -> Generator[str, None, None]:
    """
    Convert async generator to sync generator for Flask.

    Args:
        async_gen: Async generator that yields streaming chunks

    Yields:
        Streaming chunks as strings
    """
    # Create a new event loop for this thread
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        # Clean up the async generator
        try:
            loop.run_until_complete(async_gen.aclose())
        except:
            pass


def run_async_in_thread(
    async_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any
) -> Any:
    """
    Run an async function in a new event loop for the current thread.

    Args:
        async_func: The async function to run
        *args, **kwargs: Arguments to pass to the async function

    Returns:
        The result of the async function
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(async_func(*args, **kwargs))
