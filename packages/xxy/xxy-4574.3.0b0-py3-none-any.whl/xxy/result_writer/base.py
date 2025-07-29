from types import TracebackType
from typing import Optional, Type

from xxy.types import Entity, Query


class ResultWriterBase:
    def __enter__(self) -> "ResultWriterBase":
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> None:
        pass

    def write(self, query: Query, result: Entity, reference: Entity) -> None:
        raise NotImplementedError()
