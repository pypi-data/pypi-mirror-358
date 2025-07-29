from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Query:
    company: str
    date: str
    entity_name: str


@dataclass
class Entity:
    value: str
    reference: str


class RongdaDoc(TypedDict):
    doc_id: str
    title: str
    content_clip: str
