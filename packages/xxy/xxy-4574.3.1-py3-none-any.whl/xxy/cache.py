import asyncio
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Dict, Optional, Tuple, Type

from xxy.chunker import TextChunker

# 全局变量
_chunkers: Dict[str, Tuple[TextChunker, int]] = {}  # (chunker, reference_count)
_cache_lock = asyncio.Lock()


class DocumentChunker:
    """
    文档chunker的上下文管理器，自动处理缓存的创建和清理
    使用引用计数来管理多个实例共享同一个chunker的情况
    """

    def __init__(
        self, doc_id: str, text: str, chunk_size: int = 1000, overlap: int = 100
    ):
        self.doc_id = doc_id
        self.text = text
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunker: Optional[TextChunker] = None
        self._created_new = False

    async def __aenter__(self) -> TextChunker:
        """进入上下文时创建或获取chunker并增加引用计数"""
        async with _cache_lock:
            if self.doc_id in _chunkers:
                # 如果已存在，获取现有的chunker并增加引用计数
                self.chunker, ref_count = _chunkers[self.doc_id]
                _chunkers[self.doc_id] = (self.chunker, ref_count + 1)
                self._created_new = False
            else:
                # 如果不存在，创建新的chunker
                self.chunker = TextChunker(self.text, self.chunk_size, self.overlap)
                _chunkers[self.doc_id] = (self.chunker, 1)
                self._created_new = True

            return self.chunker

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """退出上下文时减少引用计数，但不删除chunker"""
        async with _cache_lock:
            if self.doc_id in _chunkers:
                chunker, ref_count = _chunkers[self.doc_id]
                new_ref_count = ref_count - 1


async def get_chunker(doc_id: str) -> Optional[TextChunker]:
    """
    从缓存中获取指定文档的chunker

    Args:
        doc_id: 文档ID

    Returns:
        TextChunker实例，如果不存在则返回None
    """
    async with _cache_lock:
        if doc_id in _chunkers:
            return _chunkers[doc_id][0]  # 返回chunker，不返回引用计数
        return None


def load_chunker(
    doc_id: str, text: str, chunk_size: int = 1000, overlap: int = 100
) -> DocumentChunker:
    """
    创建新的chunker上下文管理器

    Args:
        doc_id: 文档ID
        text: 文档文本内容
        chunk_size: 每个chunk的大小（字符数）
        overlap: chunk之间的重叠字符数

    Returns:
        DocumentChunker上下文管理器
    """
    return DocumentChunker(doc_id, text, chunk_size, overlap)


async def chunker_gc() -> int:
    """
    垃圾回收函数，清理引用计数为0的chunker

    Returns:
        清理的chunker数量
    """
    async with _cache_lock:
        to_remove = []
        for doc_id, (chunker, ref_count) in _chunkers.items():
            if ref_count <= 0:
                to_remove.append(doc_id)

        for doc_id in to_remove:
            del _chunkers[doc_id]

        return len(to_remove)


async def get_cached_doc_ids() -> list[str]:
    """
    获取所有已缓存的文档ID列表

    Returns:
        文档ID列表
    """
    async with _cache_lock:
        return list(_chunkers.keys())


async def get_chunker_info() -> Dict[str, int]:
    """
    获取所有chunker的引用计数信息

    Returns:
        文档ID到引用计数的映射
    """
    async with _cache_lock:
        return {doc_id: ref_count for doc_id, (chunker, ref_count) in _chunkers.items()}


async def has_chunker(doc_id: str) -> bool:
    """
    检查指定文档的chunker是否已缓存

    Args:
        doc_id: 文档ID

    Returns:
        是否存在缓存
    """
    async with _cache_lock:
        return doc_id in _chunkers
