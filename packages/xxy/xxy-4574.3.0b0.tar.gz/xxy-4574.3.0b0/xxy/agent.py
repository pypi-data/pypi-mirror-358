from typing import Any, Awaitable, List, Optional, Tuple, cast

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from xxy.client import get_slm
from xxy.data_source.base import DataSourceBase
from xxy.result_writer.base import ResultWriterBase
from xxy.selector import select_entity
from xxy.types import Entity, Query


async def generate_search_keywords(query: Query) -> List[str]:
    """Generate search keywords using LLM for financial information extraction.

    Args:
        query: The query containing the entity name to generate keywords for.

    Returns:
        List[str]: A list of search keywords that would help find relevant financial information.
                  These are variations of the entity name that might appear in financial documents.

    Example:
        For a query with entity_name "revenue", it might return ["revenue", "sales", "income", "turnover"]
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a search expert. Given a query about a company's financial information, 
        generate a list of search keywords that would help find the relevant information.
        The keywords should be variations of the entity name that might appear in financial documents.
        Note the entity is single thing, if you get something like "revenue/product1", you should help generate keywords to extract the revenue of product1 instead of the revenue of the company.
        Output should be a JSON array of strings.
        Example: For "revenue", you might generate ["revenue", "sales", "income", "turnover"]""",
            ),
            ("human", "Entity: {entity_name}\nGenerate search keywords:"),
        ]
    )

    chain = prompt | get_slm() | JsonOutputParser()
    keywords = await chain.ainvoke({"entity_name": query.entity_name})
    return cast(List[str], keywords)


async def evaluate_search_results(
    query: Query, candidates: List[Entity], search_keywords: List[str]
) -> Tuple[bool, Optional[str]]:
    """Evaluate search results to determine if they provide sufficient information.

    Args:
        query: The original query containing the entity to search for.
        candidates: List of potential results found in the documents.
        search_keywords: List of keywords used in the search.

    Returns:
        Tuple[bool, Optional[str]]: A tuple containing:
            - bool: Whether the results are sufficient to answer the query
            - Optional[str]: Suggested new keywords to try if results are insufficient

    Note:
        The function prioritizes high-precision values (down to 1 or 0.1) over rounded values.
        If all available values are in millions/billions/万元/亿元, the results are considered insufficient.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a financial information evaluator. Given search results and the original query,
        determine if the results are good enough to answer the query.
        Note the value is single number, if you get something like "revenue/product1", you should detect whether it good enough to extract the revenue of product1 instead of the revenue of the company.
        You should prioritize high-precision values (down to 1 or 0.1) over rounded values with units like million or billion.
        If all available values are in millions/billions/万元/亿元, the results are not sufficient and you should suggest new keywords to find more precise values.
        Output should be a JSON object with:
        - "is_sufficient": boolean indicating if results are good enough
        - "reason": string explaining why
        - "suggested_keywords": array of new keywords to try if not sufficient""",
            ),
            (
                "human",
                """Query: {query}
        Search Keywords Used: {keywords}
        Results:
        {results}
        
        Evaluate if these results are sufficient:""",
            ),
        ]
    )

    results_text = "\n".join(
        [f"Reference: {c.reference}\nValue: {c.value}" for c in candidates]
    )

    chain = prompt | get_slm() | JsonOutputParser()
    evaluation = await chain.ainvoke(
        {
            "query": query.entity_name,
            "keywords": search_keywords,
            "results": results_text,
        }
    )

    return evaluation["is_sufficient"], evaluation.get("suggested_keywords")


async def summarize_results(
    query: Query, candidates: List[Entity]
) -> Tuple[Entity, Entity]:
    """Summarize search results to get the most accurate financial value.

    Args:
        query: The original query containing company, date, and entity information.
        candidates: List of potential results found in the documents.

    Returns:
        Tuple[Entity, Entity]: A tuple containing:
            - Entity: The summarized value with reference index
            - Entity: The full reference from the candidates list

    Note:
        The function prioritizes high-precision values (down to 1 or 0.1) over rounded values.
        For values with units, it converts them to their actual numerical values:
        - billion -> multiply by 1,000,000,000
        - million -> multiply by 1,000,000
        - "亿元" -> multiply by 100,000,000
        - "万元" -> multiply by 10,000

    Example:
        If a result shows "1.5 billion", it will be converted to 1,500,000,000
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a compay's financial report information summarizer. Given multiple search results,
        analyze them and provide a single, most accurate answer about the company's financial performance on this entity at that time.
        Note the value is single number, if you get something like "revenue/product1", you should extract the revenue of product1 instead of the revenue of the company.
        You should ALWAYS prioritize high-precision values (down to 1 or 0.1) over rounded values with units like million or billion.
        For any values with units like billion, million, "万元", "亿元", convert them to their actual numerical values:
        - billion -> multiply by 1,000,000,000
        - million -> multiply by 1,000,000
        - "亿元" -> multiply by 100,000,000
        - "万元" -> multiply by 10,000
        If multiple values exist, always select the one with the highest precision (e.g., exact value rather than rounded estimates).
        Output should be a JSON object with:
        - "reason": explanation of why this is the best answer
        - "reference_index": the index of the most relevant reference from the results (0-based)
        - "value": the exact number from the most relevant result as a numeric value (int or float, not a string)""",
            ),
            (
                "human",
                """Query: {query}
        Results:
        {results}
        
        Provide the best consolidated answer. For the value field, output ONLY the exact value without any additional text:""",
            ),
        ]
    )

    results_text = "\n".join(
        [
            f"Index: {i}\nReference: {c.reference}\nValue: {c.value}"
            for i, c in enumerate(candidates)
        ]
    )

    chain = prompt | get_slm() | JsonOutputParser()
    summary = await chain.ainvoke(
        {
            "query": f"Company: {query.company}, Date: {query.date}, Entity: {query.entity_name}",
            "results": results_text,
        }
    )

    reference_index = summary["reference_index"]
    reference_entity = candidates[reference_index]
    logger.debug("reason: {reason}", reason=summary["reason"])
    # Extract just filename and page number from reference
    ref_parts = reference_entity.reference.split(":")
    if len(ref_parts) == 2:
        ref_text = f"{ref_parts[0]}:{ref_parts[1]}"
    else:
        ref_text = reference_entity.reference

    return (Entity(value=summary["value"], reference=ref_text), reference_entity)


async def search_entity(
    data_source: DataSourceBase, query: Query
) -> Tuple[Entity, Entity]:
    """Search for a specific financial entity in the data source.

    Args:
        data_source: The data source to search in (e.g., PDF documents).
        query: The query containing company, date, and entity information.

    Returns:
        Tuple[Entity, Entity]: A tuple containing:
            - Entity: The search result with value and reference
            - Entity: The reference entity with full details

    Note:
        The function will:
        1. Generate search keywords
        2. Try up to 3 times to find sufficient results
        3. Evaluate results for precision and relevance
        4. Summarize the best result found

    Example:
        >>> query = Query(company="AAPL", date="2023", entity_name="revenue")
        >>> result, reference = await search_entity(data_source, query)
    """
    result = Entity(value="N/A", reference="N/A")
    reference_entity = Entity(value="N/A", reference="N/A")

    try:
        # Initial search keywords
        search_keywords = await generate_search_keywords(query)
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            logger.info(
                f"Search attempt {attempt + 1} with keywords: {search_keywords}"
            )

            # Search for each keyword and combine results
            all_candidates = []
            for keyword in search_keywords:
                search_query = Query(
                    company=query.company, date=query.date, entity_name=keyword
                )
                candidates = await data_source.search(search_query)
                if candidates:
                    all_candidates.extend(candidates)

            if not all_candidates:
                logger.debug(f"No candidates found for keywords: {search_keywords}")
                attempt += 1
                continue

            # Evaluate results
            is_sufficient, new_keywords = await evaluate_search_results(
                query, all_candidates, search_keywords
            )

            if is_sufficient:
                # Summarize the results to get the best answer
                result, reference_entity = await summarize_results(
                    query, all_candidates
                )
                logger.info(
                    "Found sufficient results on attempt {}: {}; {}",
                    attempt + 1,
                    reference_entity.reference,
                    reference_entity.value,
                )
                break

            if new_keywords:
                search_keywords = cast(List[str], new_keywords)
            attempt += 1

        if attempt >= max_attempts:
            logger.warning(f"Max search attempts reached for query: {query}")

    except Exception as e:
        logger.exception(f"Error in processing query: {query}", exc_info=e)

    return result, reference_entity


async def build_table(
    data_source: DataSourceBase,
    companys: List[str],
    dates: List[str],
    names: List[str],
    writer: ResultWriterBase,
) -> None:
    """Build a table of financial information for multiple companies, dates, and entities.

    Args:
        data_source: The data source to search in (e.g., PDF documents).
        companys: List of company identifiers to search for.
        dates: List of dates to search for.
        names: List of entity names to search for.
        writer: The result writer to use for output.

    Note:
        - If companys list is empty, it will search for "any" company
        - For each combination of company, date, and entity name, it will:
          1. Create a query
          2. Search for the entity
          3. Write the result using the provided writer
    """
    companys_to_search = companys if len(companys) > 0 else ["any"]
    for company in companys_to_search:
        for date in dates:
            for name in names:
                query = Query(company=company, date=date, entity_name=name)
                result, reference_eneity = await search_entity(data_source, query)
                writer.write(query, result, reference_eneity)
