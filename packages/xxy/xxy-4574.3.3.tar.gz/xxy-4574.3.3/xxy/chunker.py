import asyncio
import json
import re
from functools import cache
from os import environ
from typing import Annotated, Any, Dict, List, Literal, Tuple, TypedDict, Union


class TextChunker:
    """
    A class for chunking long text into manageable segments and providing search/retrieval functionality.
    """

    def __init__(self, text: str, chunk_size: int = 1000, overlap: int = 10000):
        """
        Initialize the TextChunker with a long string.

        Args:
            text (str): The long text to be chunked
            chunk_size (int): Size of each chunk in characters (default: 1000)
            overlap (int): Number of overlapping characters between chunks (default: 100)
        """
        self.text = text
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[str] = []
        self._create_chunks()

    def _create_chunks(self) -> None:
        """
        Create chunks from the input text with specified size and overlap.
        """
        if not self.text:
            return

        start = 0
        while start < len(self.text):
            end = start + self.chunk_size

            # If this is not the last chunk and we're not at the end of text
            if end < len(self.text):
                # Try to find a good breaking point (sentence end, paragraph, etc.)
                break_point = self._find_break_point(self.text[start:end])
                if break_point != -1:
                    end = start + break_point

            chunk = self.text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                self.chunks.append(chunk)

            # Move start position with overlap consideration
            if end >= len(self.text):
                break
            start = max(start + self.chunk_size - self.overlap, start + 1)

    def _find_break_point(self, text: str) -> int:
        """
        Find a good breaking point in the text (sentence end, paragraph break, etc.).

        Args:
            text (str): Text to find break point in

        Returns:
            int: Position of break point, or -1 if no good break point found
        """
        # Look for sentence endings in the last 200 characters
        search_start = max(0, len(text) - 200)
        search_text = text[search_start:]

        # Look for paragraph breaks first
        paragraph_break = search_text.rfind("\n\n")
        if paragraph_break != -1:
            return search_start + paragraph_break

        # Look for sentence endings
        sentence_endings = [". ", "! ", "? ", ".\n", "!\n", "?\n"]
        best_break = -1

        for ending in sentence_endings:
            pos = search_text.rfind(ending)
            if pos != -1:
                best_break = max(best_break, search_start + pos + len(ending))

        return best_break if best_break != -1 else -1

    def search(
        self, keywords: Union[str, List[str]], case_sensitive: bool = False
    ) -> List[int]:
        """
        Search for chunks containing specified keywords.

        Args:
            keywords (Union[str, List[str]]): Keywords to search for
            case_sensitive (bool): Whether search should be case sensitive

        Returns:
            List[int]: Ordered list of chunk indices containing the keywords
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        matching_indices = []

        for i, chunk in enumerate(self.chunks):
            search_text = chunk if case_sensitive else chunk.lower()
            search_keywords = (
                keywords if case_sensitive else [kw.lower() for kw in keywords]
            )

            # Check if any keyword is found in the chunk
            if any(keyword in search_text for keyword in search_keywords):
                matching_indices.append(i)

        return matching_indices

    def retrieval(self, index: int) -> str:
        """
        Retrieve a chunk by its index.

        Args:
            index (int): Index of the chunk to retrieve

        Returns:
            str: The chunk at the specified index

        Raises:
            IndexError: If index is out of range
        """
        if not 0 <= index < len(self.chunks):
            raise IndexError(
                f"Index {index} is out of range. Valid range: 0-{len(self.chunks)-1}"
            )

        return self.chunks[index]

    def get_chunk_count(self) -> int:
        """
        Get the total number of chunks.

        Returns:
            int: Total number of chunks
        """
        return len(self.chunks)

    def get_chunk_info(self, index: int) -> Dict[str, Any]:
        """
        Get information about a specific chunk.

        Args:
            index (int): Index of the chunk

        Returns:
            Dict[str, Any]: Information about the chunk including index, length, and preview
        """
        if not 0 <= index < len(self.chunks):
            raise IndexError(
                f"Index {index} is out of range. Valid range: 0-{len(self.chunks)-1}"
            )

        chunk = self.chunks[index]
        return {
            "index": index,
            "length": len(chunk),
            "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk,
            "has_previous": index > 0,
            "has_next": index < len(self.chunks) - 1,
        }
