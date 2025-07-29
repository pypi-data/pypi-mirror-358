from dataclasses import dataclass
from enum import Enum

__all__ = ["parse_markdown"]

class TLEntityType(Enum):
    CODE = "code"
    PRE = "pre"
    STRIKETHROUGH = "strikethrough"
    TEXT_LINK = "text_link"
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    SPOILER = "spoiler"
    CUSTOM_EMOJI = "custom_emoji"

@dataclass
class RawEntity:
    type: TLEntityType
    offset: int
    length: int
    language: str | None = ...
    url: str | None = ...
    document_id: int | None = ...
    def to_tlrpc_object(self): ...
    def __init__(
        self, type, offset, length, language=..., url=..., document_id=...
    ) -> None: ...

@dataclass
class ParsedMessage:
    text: str
    entities: tuple[RawEntity, ...]
    def __init__(self, text, entities) -> None: ...

def parse_markdown(markdown: str) -> ParsedMessage: ...
