import csv
from io import TextIOWrapper
from itertools import groupby
from types import TracebackType
from typing import List, Optional, Tuple, Type

from xxy.result_writer.base import ResultWriterBase
from xxy.types import Entity, Query


class CsvResultWriter(ResultWriterBase):
    datas: list[Tuple[Query, Entity, Entity]] = []

    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    def __enter__(self) -> "CsvResultWriter":
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> None:
        with open(self.output_path, "w") as fd:

            writer = csv.writer(fd)
            cnv = sorted(
                self.datas,
                key=lambda x: x[0].company + "_" + x[0].entity_name + "_" + x[0].date,
            )

            line = ["Year", "Entity"] + sorted(set([x[0].date for x in cnv]))
            ref_lines: List[List[str]] = []
            writer.writerow(line)
            for c, nv in groupby(cnv, key=lambda x: x[0].company):
                for n, v in groupby(nv, key=lambda x: x[0].entity_name):
                    tv = list(v)
                    line = [c, n] + [x[1].value for x in tv]
                    writer.writerow(line)
                    line = [c, n] + [x[1].reference for x in tv]
                    ref_lines.append(line)

            writer.writerow(["References"])
            for line in ref_lines:
                writer.writerow(line)

    def write(self, query: Query, result: Entity, reference: Entity) -> None:
        self.datas.append((query, result, reference))
