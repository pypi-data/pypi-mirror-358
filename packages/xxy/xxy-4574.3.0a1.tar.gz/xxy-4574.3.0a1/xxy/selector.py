from typing import Awaitable, List, Tuple

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models.base import BaseChatOpenAI
from loguru import logger

from xxy.client import get_llm
from xxy.types import Entity, Query


async def select_entity(query: Query, entities: List[Entity]) -> Tuple[Entity, int]:
    selector = (
        ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "User gives a list of financial reports contents to search for certain financial value of a company. Please select the most relevant value based on the following rules:\n"
                        '- output should be formatted as JSON like {{"value": 1453.2, "index": 1, "reason": ""}}, the index should match the one provided by the user, and the reason is a string to explain why.\n'
                        "- The value should match what the user is searching for. If the data has units such as thousands or millions, 万元, 千, convert them into their actual numerical values.\n"
                        "- Input is usually a table in text format, you need to be careful on table headers, as they may contain important information such as units. The table header and content may be split into multipy lines. Always reconstruct and interpret the data as a structured table.\n"
                        "- If multiple values exist, select the one with the highest precision (e.g., exact value rather than rounded estimates).\n"
                        "- Always prioritize the latest available data for the current season over past periods.\n"
                        '- If no data supports the requested value or if the data is from the wrong period, return "value": null and provide an explanation in reason.\n'
                    ),
                ),
                (
                    "human",
                    "Search for {entity_name} about company {company} for {date}\n\nHere are the candidates:\n{candidates}",
                ),
            ]
        )
        | get_llm()
        | JsonOutputParser()
    )

    candidates_desc = "\n\n==============".join(
        [f"index: {ix}, file_name: {i}" for ix, i in enumerate(entities)]
    )

    llm_output = await selector.ainvoke(
        {
            "company": query.company,
            "date": query.date,
            "entity_name": query.entity_name,
            "candidates": candidates_desc,
        }
    )
    logger.trace("selector output: {}", llm_output)
    value: int = llm_output.get("value", None)
    if value is None:
        logger.warning(
            "Can not find value for {}, reason: {}",
            query,
            llm_output.get("reason", "N/A"),
        )

        return Entity(value="N/A", reference="N/A"), -1
    selected_idx = llm_output.get("index", -1)

    return (
        Entity(value=str(value), reference=entities[llm_output["index"]].reference),
        selected_idx,
    )
