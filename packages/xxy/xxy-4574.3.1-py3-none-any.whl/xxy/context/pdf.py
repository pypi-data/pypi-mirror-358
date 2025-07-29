"""
Based on from following source:
from llama_index.readers.file import PDFReader
"""

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fsspec import AbstractFileSystem  # type: ignore[import-untyped]
from llama_index.core.readers.base import BaseReader
from llama_index.core.readers.file.base import get_default_fs, is_default_fs
from llama_index.core.schema import Document


class ContextAwarePDFReader(BaseReader):
    """PDF parser using pdfplumber for improved text extraction."""

    def __init__(
        self,
        retain_layout: Optional[bool] = True,
    ) -> None:
        """
        Initialize PDFReader.

        Args:
            retain_layout (Optional[bool]): If True, attempts to maintain PDF layout during text
                extraction. Defaults to True.
        """
        self.retain_layout = retain_layout

    def load_data(
        self,
        file: Path,
        extra_info: Optional[Dict[str, Any]] = None,
        fs: Optional[AbstractFileSystem] = None,
        include_tables: bool = True,
    ) -> List[Document]:
        """Parse PDF file using pdfplumber.

        Args:
            file: Path to the PDF file
            extra_info: Additional metadata to include in the documents
            fs: Optional filesystem to use
            include_tables: Whether to extract and include tables in the output. Defaults to True.

        Returns:
            List of Document objects containing the extracted text and tables (if include_tables is True)
        """
        if not isinstance(file, Path):
            file = Path(file)

        try:
            import pdfplumber  # type: ignore[import-not-found]
        except ImportError:
            raise ImportError(
                "pdfplumber is required to read PDF files: `pip install pdfplumber`"
            )

        fs = fs or get_default_fs()
        with fs.open(file, "rb") as fp:
            # Load the file in memory if the filesystem is not the default one
            stream = fp if is_default_fs(fs) else io.BytesIO(fp.read())

            # Create a PDF object
            with pdfplumber.open(stream) as pdf:
                docs = []

                # Process outline into page-to-section mapping if available
                page_sections: Dict[int, str] = {}
                if hasattr(pdf, "outline") and pdf.outline:
                    self._build_page_sections(pdf.outline, page_sections)

                for page_num, page in enumerate(pdf.pages, 1):
                    # prepare page info
                    page_info = {
                        "page_label": str(page_num),
                        "file_name": file.name,
                        "content_type": "text",
                    }
                    text_prefix = f"Page {page_num}\n"

                    # Add section information if available
                    if page_num in page_sections:
                        page_info["section"] = page_sections[page_num]
                        text_prefix += f"Section: {page_info['section']}\n"

                    if extra_info is not None:
                        page_info.update(extra_info)

                    # Extract text from the page
                    if self.retain_layout:
                        page_text = page.extract_text(layout=True)
                    else:
                        page_text = page.extract_text()

                    docs.append(
                        Document(
                            text=text_prefix + page_text.strip(), extra_info=page_info
                        )
                    )

                    # Extract tables from the page if requested
                    if include_tables:
                        tables: List[List[List[Optional[str]]]] = page.extract_tables()
                        for table_idx, table in enumerate(tables):
                            table_info = page_info.copy()
                            table_info["content_type"] = "table"
                            for t in self.table_to_text(table):
                                docs.append(
                                    Document(
                                        text=text_prefix + t, extra_info=table_info
                                    )
                                )

                return docs

    def _build_page_sections(
        self,
        outline: List[Dict[str, Any]],
        page_sections: Dict[int, str],
        current_path: str = "",
    ) -> None:
        """Build a mapping of page numbers to their section paths from the outline.

        Args:
            outline: List of outline items from pdfplumber
            page_sections: Dictionary to store page to section mappings
            current_path: Current section path (for nested sections)
        """
        for item in outline:
            title = item.get("title", "").strip()
            page = item.get("page_number")

            if title and page is not None:
                # Build the full section path
                section_path = f"{current_path}/{title}" if current_path else title
                page_sections[page] = section_path

                # Process nested items with updated path
                children = item.get("children", [])
                if children:
                    self._build_page_sections(children, page_sections, section_path)

    def _process_outline(self, outline: List[Dict[str, Any]], level: int = 0) -> str:
        """Process PDF outline/bookmarks into a structured text format.

        Args:
            outline: List of outline items from pdfplumber
            level: Current indentation level (for nested bookmarks)

        Returns:
            Formatted string containing the table of contents
        """
        result = []
        for item in outline:
            # Basic item info
            title = item.get("title", "").strip()
            page = item.get("page_number", "")

            if title:
                # Add indentation based on level
                indent = "  " * level
                entry = f"{indent}- {title}"
                if page:
                    entry += f" (Page {page})"
                result.append(entry)

            # Process nested items
            children = item.get("children", [])
            if children:
                child_text = self._process_outline(children, level + 1)
                if child_text:
                    result.append(child_text)

        return "\n".join(result)

    def table_to_text(
        self, table: List[List[Optional[str]]], split_size: Tuple[int, int] = (5, 5)
    ) -> List[str]:
        """Convert a table to a string.
        When the table is small, e.g. small then 5 columns and 5 rows, we can convert the table to a string.
        Otherwise, we split the table into a list of strings, each representing single cell in the table with column and row name.
        """
        # Handle empty tab
        if not table or not table[0]:
            return []

        rows = len(table)
        cols = len(table[0])

        # For small tables, convert to simple text representation
        if rows <= split_size[0] and cols <= split_size[1]:
            # Convert the entire table to a single string with rows separated by newlines
            table_text = "\n".join(
                "\t".join(str(cell) if cell is not None else "" for cell in row)
                for row in table
                if any(cell is not None and str(cell).strip() for cell in row)
            )
            return [table_text] if table_text else []

        # For larger tables, create cell-by-cell representation
        result = []
        for i, row in enumerate(table):
            for j, cell in enumerate(row):
                if cell is None or str(cell).strip() == "":
                    continue
                # Create a string that identifies the cell location and content
                cell_text = f"Row {i+1}, Column {j+1}: {cell}"
                result.append(cell_text)

        return result
