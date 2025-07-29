from pathlib import Path
from typing import Dict, List, Optional, Tuple, cast

from langchain_core.documents import Document as LangchainDocument
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.data_structs.data_structs import IndexDict
from llama_index.core.indices.base import BaseIndex
from llama_index.core.retrievers import BaseRetriever, QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import Document
from llama_index.core.settings import Settings, _Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.readers.file import PDFReader
from llama_index.retrievers.bm25 import BM25Retriever  # type: ignore[import-untyped]
from loguru import logger

from xxy.client import get_slm
from xxy.config import get_cache_path, load_config
from xxy.context.pdf import ContextAwarePDFReader
from xxy.data_source.base import DataSourceBase
from xxy.types import Entity, Query


def convert_to_langchain_docs(docs: List[Document]) -> List[LangchainDocument]:
    """Convert llama_index Documents to langchain Documents."""
    return [
        LangchainDocument(page_content=doc.text, metadata=doc.metadata) for doc in docs
    ]


def convert_to_llama_docs(docs: List[LangchainDocument]) -> List[Document]:
    """Convert langchain Documents back to llama_index Documents."""
    return [Document(text=doc.page_content, metadata=doc.metadata) for doc in docs]


class IndexCache:
    """Cache for document indices to avoid reprocessing the same files."""

    # Increment this when making changes that require regenerating the index
    VERSION = "1.3"

    def __init__(self) -> None:
        pass

    async def get_index(self, select_file: Path) -> BaseIndex[IndexDict]:
        logger.trace("get_index for {}", select_file)
        index_path = get_cache_path(select_file)
        if index_path.exists():
            logger.debug("load index from cache: {}", index_path)
            storage_context = StorageContext.from_defaults(
                persist_dir=index_path.as_posix()
            )

            # Check version
            try:
                with open(index_path / "version.txt", "r") as f:
                    cached_version = f.read().strip()
                if cached_version != self.VERSION:
                    logger.info(
                        "Cache version mismatch ({} != {}), regenerating index",
                        cached_version,
                        self.VERSION,
                    )
                    return await self._regenerate_index(select_file, index_path)
            except FileNotFoundError:
                logger.info("No version file found, regenerating index")
                return await self._regenerate_index(select_file, index_path)

            index = load_index_from_storage(
                storage_context=storage_context, embed_model=self._get_embed_model()
            )
            return index
        else:
            logger.debug("load index from scratch: {}", select_file)
            return await self._regenerate_index(select_file, index_path)

    async def _regenerate_index(
        self, select_file: Path, index_path: Path
    ) -> BaseIndex[IndexDict]:
        """Generate a new index and save it with version information."""
        index = await self._get_index(select_file)
        logger.trace("persist index to {}", index_path.as_posix())
        index.storage_context.persist(index_path.as_posix())

        # Save version information
        with open(index_path / "version.txt", "w") as f:
            f.write(self.VERSION)

        return index

    async def _get_index(self, select_file: Path) -> VectorStoreIndex:
        documents = ContextAwarePDFReader().load_data(
            select_file, {"file_path": str(select_file)}, include_tables=False
        )

        # Convert to langchain documents for text splitting
        langchain_docs = convert_to_langchain_docs(documents)

        # Create a text splitter with chunk size and overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Apply the chunker to documents and convert back to llama_index documents
        chunked_documents = convert_to_llama_docs(
            text_splitter.split_documents(langchain_docs)
        )

        parser = Settings.node_parser
        nodes = parser.get_nodes_from_documents(chunked_documents)
        logger.debug(
            f"Loaded {len(nodes)} document nodes from {select_file}, including {len([_ for _ in nodes if _.metadata['content_type'] == 'table'])} tables "
        )
        return VectorStoreIndex(nodes=nodes, embed_model=self._get_embed_model())

    def _get_embed_model(self) -> AzureOpenAIEmbedding:
        config = load_config()
        embed = AzureOpenAIEmbedding(
            azure_endpoint=config.llm.openai_api_base,
            azure_deployment=config.llm.embedding.deployment_id,
            api_key=config.llm.openai_api_key,
            api_version=config.llm.openai_api_version,
        )
        return embed


class FolderDataSource(DataSourceBase):
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.index_cache = IndexCache()
        self.retriever: Optional[BaseRetriever] = None
        self._file_selection_cache: Dict[Tuple[str, str], Path] = {}

    async def search(self, query: Query) -> List[Entity]:
        files = await self.select_file(query)
        if files is None:
            return []
        retriever = await self.get_retriever(files)
        response = await retriever.aretrieve(query.entity_name)
        return [
            Entity(
                value=node.text,
                reference=node.metadata["file_path"]
                + ":"
                + node.metadata["page_label"],
            )
            for node in response
        ]

    async def get_retriever(self, files: Path) -> BaseRetriever:
        if self.retriever is None:
            index = await self.index_cache.get_index(files)
            vector_retriever = index.as_retriever()
            bm25_retriever = BM25Retriever.from_defaults(
                docstore=index.docstore, similarity_top_k=2
            )
            self.retriever = QueryFusionRetriever(
                [vector_retriever, bm25_retriever],
                similarity_top_k=2,
                num_queries=1,  # set this to 1 to disable query generation
                mode=FUSION_MODES.RECIPROCAL_RANK,
                use_async=True,
                verbose=True,
            )
        return self.retriever

    async def select_file(self, query: Query) -> Optional[Path]:
        # Check cache first
        cache_key = (query.company, query.date)
        if cache_key in self._file_selection_cache:
            logger.trace(
                "Using cached file selection for company: {}, date: {}",
                query.company,
                query.date,
            )
            return self._file_selection_cache[cache_key]

        candidates = list(Path(self.folder_path).glob("**/*.pdf", case_sensitive=False))
        selector = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        (
                            "User gives a list of financial reports to search for infomation of a company. Please select the one that with following rule:\n"
                            '- output should be formatted as JSON like {{"index": 1, "reason": ""}}\n'
                            "- the index should be the same as user given, and the reason is a string to explain why\n"
                        ),
                    ),
                    (
                        "human",
                        "Search report about company {company} for {date}\n\nHere are the candidates:\n{candidates}",
                    ),
                ]
            )
            | get_slm()
            | JsonOutputParser()
        )

        candidates_desc = "\n".join(
            [f"index: {ix}, file_name: {i}" for ix, i in enumerate(candidates)]
        )

        llm_output = await selector.ainvoke(
            {
                "company": query.company,
                "date": query.date,
                "candidates": candidates_desc,
            }
        )
        logger.trace("selector output: {}", llm_output)
        selected_idx: int = llm_output.get("index", -1)

        if selected_idx == -1:
            logger.warning(
                "No file selected, reason: {}", llm_output.get("reason", "N/A")
            )
            return None

        selected_file = candidates[selected_idx]

        logger.info("selected file: {}", selected_file)
        # Cache the selection
        self._file_selection_cache[cache_key] = selected_file
        logger.trace(
            "Cached file selection for company: {}, date: {}", query.company, query.date
        )

        return selected_file
