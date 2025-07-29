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
from langgraph.prebuilt import ToolNode
from loguru import logger
from pydantic import BaseModel, Field
from rongda_mcp_server.api import ReportType, comprehensive_search, download_report_html
from rongda_mcp_server.login import login
from rongda_mcp_server.models import FinancialReport

from xxy.agents.analysis_agent import AgentState, create_document_agent
from xxy.agents.search_agent import SearchAgentState, create_search_agent
from xxy.chunker import TextChunker
from xxy.client import get_llm, get_slm
from xxy.config import load_config
from xxy.rongda_session import get_rongda_seesion
from xxy.stream import send_reasoning
from xxy.types import RongdaDoc


async def process_document_question(
    user_question: str,
    company_code: List[str],
    doc_id: Optional[str] = None,
    messages: List[AIMessage | HumanMessage | ToolMessage] = [],
) -> str:
    """
    Process a user question - first search for relevant documents, then analyze the selected document

    Args:
        user_question: The user's question about financial documents
        company_code: List of company codes to search in
        doc_id: Optional specific document ID to analyze (skips search phase)

    Returns:
        The agent's answer to the question
    """
    logger.debug(f"🚀 Starting two-phase document processing")
    logger.debug(f"❓ User Question: {user_question}")
    logger.debug(f"🏢 Company codes: {company_code}")

    selected_doc_id = doc_id

    # Phase 1: Search for documents (if doc_id not provided)
    if not selected_doc_id:
        logger.info("🔍 Phase 1: Searching for relevant documents...")

        # Create search agent
        search_agent = create_search_agent()

        # Initialize search state
        search_state = SearchAgentState(
            user_question=user_question,
            company_code=company_code,
            messages=messages,
            found_documents=[],
            selected_doc_id="",
        )

        # Run search agent
        try:
            logger.info("🔍 Running document search workflow...")
            final_search_state = await search_agent.ainvoke(search_state)
            selected_doc_id = final_search_state.get("selected_doc_id")

            if not selected_doc_id:
                logger.warning("⚠️ No document selected by search agent")
                return "I was unable to find a relevant document for your question. Please try rephrasing your question or providing more specific keywords."

            logger.info(
                f"✅ Search phase completed. Selected document: {selected_doc_id}"
            )

        except Exception as e:
            logger.exception("❌ Error during document search")
            return f"An error occurred while searching for documents: {str(e)}"
    else:
        logger.info(
            f"📄 Skipping search phase - using provided doc_id: {selected_doc_id}"
        )

    # Phase 2: Analyze the selected document
    logger.info(f"📊 Phase 2: Analyzing document {selected_doc_id}...")

    # Create analysis agent
    logger.trace("🤖 Creating document analysis agent...")
    analysis_agent = create_document_agent()

    # Initialize analysis state
    analysis_state = AgentState(
        doc_id=selected_doc_id,
        user_question=user_question,
        messages=messages,
        document_loaded=False,
        final_answer="",
        found_documents=[],
        selected_doc_id="",
    )
    logger.trace("📊 Analysis state created")

    # Run analysis agent
    try:
        logger.trace("🎯 Running document analysis workflow...")
        final_analysis_state = await analysis_agent.ainvoke(analysis_state)

        # Return the final answer
        if final_analysis_state.get("final_answer"):
            logger.info(f"✅ Analysis completed successfully")
            return cast(str, final_analysis_state["final_answer"])
        else:
            logger.warning("⚠️ No final answer provided by analysis agent")
            return "I was unable to provide a complete answer to your question. Please try rephrasing or asking a more specific question."

    except Exception as e:
        logger.exception(f"❌ Error during document analysis")
        return f"An error occurred while analyzing the document: {str(e)}"
    finally:
        # TODO: ugly cleanup, maybe use a context manager instead
        if get_rongda_seesion.session:  # type: ignore[attr-defined]
            await get_rongda_seesion.session.close()  # type: ignore[attr-defined]
            get_rongda_seesion.session = None  # type: ignore[attr-defined]


# Convenience function for backward compatibility
async def process_document_question_with_doc_id(doc_id: str, user_question: str) -> str:
    """
    Process a question with a specific document ID (backward compatibility)
    """
    # Clear company codes for direct document access
    return await process_document_question(
        user_question, company_code=[], doc_id=doc_id
    )


if __name__ == "__main__":
    # Example with document search
    import sys

    # logger.remove()
    # logger.add(sys.stdout, level="INFO")

    async def main() -> None:
        result = await process_document_question(
            user_question="用中文，在 2023年年度报告 里搜索 '成本构成项目'里不同\"项目\"的 成本，汇总到一张表格上，单位要精确到元\n",
            company_code=["600276 恒瑞医药"],
        )
        print(result)

    asyncio.run(main())
