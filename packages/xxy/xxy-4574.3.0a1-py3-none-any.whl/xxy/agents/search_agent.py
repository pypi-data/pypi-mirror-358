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
from langchain.tools import StructuredTool, Tool
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
from rongda_mcp_server.login import login
from rongda_mcp_server.models import FinancialReport

from xxy.chunker import TextChunker
from xxy.client import get_llm, get_slm
from xxy.config import load_config
from xxy.rongda_session import get_rongda_seesion
from xxy.stream import send_reasoning
from xxy.types import RongdaDoc

MAX_DOC_RESULT = 8


async def search_rongda_doc(
    title_keywords: List[str], content_keywords: List[str], company_code: List[str]
) -> List[RongdaDoc]:
    session = await get_rongda_seesion()
    results = await comprehensive_search(
        session,
        company_code,
        content_keywords,
        title_keywords,
        report_types=[ReportType.ANNUAL_REPORT],
    )
    result = [
        RongdaDoc(
            doc_id=result.htmlpath or "",
            title=result.title,
            content_clip=result.content,
        )
        for result in results
    ]

    if len(result) > MAX_DOC_RESULT:
        return result[:MAX_DOC_RESULT]
    else:
        return result


class SearchAgentState(TypedDict):
    """State for the document search agent"""

    user_question: str
    company_code: List[str]
    messages: List[Union[HumanMessage, AIMessage, ToolMessage]]
    found_documents: List[RongdaDoc]
    selected_doc_id: str


@tool
async def search_documents(
    title_keywords: List[str], content_keywords: List[str], company_code: List[str]
) -> str:
    """
    Search for financial documents using title and content keywords.

    Args:
        title_keywords: Keywords for document title (e.g., "年度报告")
        content_keywords: Keywords for document content (e.g., "营业收入", "分行业", "成本")
        company_code: List of company codes to search in

    Returns:
        Search results with document IDs and content clips
    """

    logger.debug(
        f"🔍 Finding documents with title: '{title_keywords}', content: '{content_keywords}', companies: {company_code}"
    )
    send_reasoning(
        f"Finding documents with title: {title_keywords}, content: {content_keywords}, companies: {company_code}"
    )

    try:
        results = await search_rongda_doc(
            title_keywords, content_keywords, company_code
        )

        if not results:
            return "No documents found matching the criteria."

        result_text = f"Found {len(results)} documents:\n"
        for i, doc in enumerate(results, 1):
            result_text += f"{i}. Document ID: {doc['doc_id']}\n"
            result_text += f"   Title: {doc['title']}\n"
            result_text += f"   Content clip: {doc['content_clip']}\n\n"

        logger.info(
            f"🔍 Found {len(results)} documents: {[doc['title'] for doc in results]}"
        )
        return result_text

    except Exception as e:
        logger.exception(f"❌ Error searching documents: {str(e)}")
        return f"Error searching documents: {str(e)}"


@tool
def select_document(doc_id: str, title: str) -> str:
    """
    Select a specific document for detailed analysis.

    Args:
        doc_id: The document ID to select for analysis

    Returns:
        Confirmation of document selection
    """
    # logger.success(f"📋 Document selected: {doc_id}")
    return f"Document selected: {doc_id}. Ready for detailed analysis."


def should_continue_search(state: SearchAgentState) -> str:
    """
    Determine whether to continue the search loop or proceed to document analysis
    """
    logger.trace("🔄 Evaluating search workflow...")

    # If a document is selected, proceed to analysis
    if state.get("selected_doc_id"):
        logger.trace("✅ Document selected - proceeding to analysis")
        return "analyze"

    # Continue searching
    logger.trace("🔄 Continuing document search...")
    return "continue"


def create_search_agent() -> CompiledStateGraph:
    """
    Create the document search agent
    """
    # Get the LLM
    llm = get_llm()

    # Search tools
    search_tools: List[Tool | StructuredTool] = cast(
        List[Tool | StructuredTool], [search_documents, select_document]
    )
    logger.debug(
        f"🔍 Search tools: {[(tool.name, tool.func) for tool in search_tools]}"
    )

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(search_tools)

    # Create system prompt for search
    search_system_prompt = f"""You are a financial document search agent. Your job is to find the most relevant financial documents for the user's question.

Available tools:
- search_documents: Search for documents using title and content keywords
- select_document: Select a specific document for detailed analysis

Guidelines for title_keywords:
- Start with 1 short keywords, if returned too many results (search returns max {MAX_DOC_RESULT} results), refine by adding more keywords
- If search gives no results, refine by reducing keywords
- Keep it simple and focused on document types
- Common financial document titles: "年度报告"
- Do NOT put complex phrases or content-specific terms in title_keywords

Guidelines for content_keywords:

- Start with 1 short keywords, if returned too many results (search returns max {MAX_DOC_RESULT} results), refine by adding more keywords
- If search gives no results, refine by reducing keywords
- Use specific terms related to the user's question
- Examples: "营业收入", "分行业", "成本", "利润", "资产", "负债"
- Can be more detailed and specific than title keywords

Strategy:
1. Analyze the user's question to understand what type of financial information they need
2. Use search_documents with appropriate title and content keywords
3. Review the search results and content clips
4. If no relevant documents found, try different keyword combinations
5. Once you find relevant documents, select the most appropriate one using select_document

Be strategic about your search - start broad, then narrow down based on results."""

    async def search_agent_node(state: SearchAgentState) -> SearchAgentState:
        """
        Search agent node that finds relevant documents
        """
        logger.trace("🔍 Search agent called - finding relevant documents")

        messages: List[BaseMessage] = [SystemMessage(content=search_system_prompt)]
        messages.extend(state["messages"])

        # Add the user question and company info if not already present
        if not any(
            isinstance(msg, HumanMessage) and state["user_question"] in msg.content
            for msg in messages
        ):
            question_msg = f"Find financial documents relevant to this question: {state['user_question']}\nCompany codes: {state['company_code']}"
            messages.append(HumanMessage(content=question_msg))

        # Get LLM response
        logger.debug("🧠 Calling LLM for document search reasoning...")
        response = await llm_with_tools.ainvoke(messages)
        logger.info(
            f"🧠 Search LLM response received with {len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0} tool calls"
        )

        # Update state with the response
        if isinstance(response, (HumanMessage, AIMessage, ToolMessage)):
            state["messages"].append(response)
        # If there are tool calls, execute them
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.trace(f"🔧 Executing {len(response.tool_calls)} search tool calls")
            for i, tool_call in enumerate(response.tool_calls, 1):
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                logger.trace(
                    f"🔧 Search Tool {i}/{len(response.tool_calls)}: {tool_name} with args: {tool_args}"
                )

                # Find and execute the tool
                tool_func = None
                for tool in search_tools:
                    if tool.name == tool_name:
                        # For async tools, the function might be in 'coroutine' attribute instead of 'func'
                        tool_func = getattr(tool, "func", None) or getattr(
                            tool, "coroutine", None
                        )
                        break

                if tool_func:
                    try:
                        logger.trace(f"⚡ Executing search tool: {tool_name}")
                        if (
                            "company_code" in tool_args
                            and tool_args["company_code"] != state["company_code"]
                        ):
                            logger.warning(f"🔧 LLM tried to modify company codes!")
                            logger.warning(
                                f"   LLM provided: {tool_args['company_code']}"
                            )
                            logger.warning(
                                f"   Using original: {state['company_code']}"
                            )
                            tool_args["company_code"] = state["company_code"]

                        # Check if tool is async
                        if asyncio.iscoroutinefunction(tool_func):
                            tool_result = await tool_func(**tool_args)
                        else:
                            tool_result = tool_func(**tool_args)

                        # Special handling for select_document tool
                        if tool_name == "select_document":
                            state["selected_doc_id"] = tool_args.get("doc_id", "")
                            title = tool_args.get("title", "")
                            send_reasoning(f"Reading {title}")
                            logger.success(
                                f"📋 Document selected: {title}: {state['selected_doc_id']}"
                            )

                        logger.trace(
                            f"✅ Search tool {tool_name} executed successfully"
                        )

                        # Add tool result to messages
                        state["messages"].append(
                            ToolMessage(
                                content=tool_result, tool_call_id=tool_call["id"]
                            )
                        )
                    except Exception as e:
                        logger.exception(f"❌ Error executing search tool {tool_name}")
                        state["messages"].append(
                            ToolMessage(
                                content=f"Error executing {tool_name}: {str(e)}",
                                tool_call_id=tool_call["id"],
                            )
                        )
                else:
                    logger.error(f"❌ Search tool not found: {tool_name}")
        else:
            logger.info("💭 No tool calls in search LLM response")

        logger.trace("🔍 Search agent node completed")
        return state

    # Create the search graph
    search_workflow = StateGraph(SearchAgentState)

    # Add search node
    search_workflow.add_node("search_agent", search_agent_node)

    # Add edges
    search_workflow.set_entry_point("search_agent")
    search_workflow.add_conditional_edges(
        "search_agent",
        should_continue_search,
        {"continue": "search_agent", "analyze": END},
    )

    return search_workflow.compile()
