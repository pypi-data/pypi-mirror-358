# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Draftjs", "Content", "ContentBlock", "ContentBlockEntityRange", "ContentBlockInlineStyleRange"]


class ContentBlockEntityRange(BaseModel):
    key: int

    length: int

    offset: int


class ContentBlockInlineStyleRange(BaseModel):
    length: int

    offset: int

    style: str


class ContentBlock(BaseModel):
    data: Dict[str, object]

    depth: int

    entity_ranges: List[ContentBlockEntityRange] = FieldInfo(alias="entityRanges")

    inline_style_ranges: List[ContentBlockInlineStyleRange] = FieldInfo(alias="inlineStyleRanges")

    key: str

    text: str

    type: str


class Content(BaseModel):
    blocks: List[ContentBlock]

    entity_map: Dict[str, object] = FieldInfo(alias="entityMap")


class Draftjs(BaseModel):
    content: Content
