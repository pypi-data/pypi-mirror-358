# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DraftjsParam", "Content", "ContentBlock", "ContentBlockEntityRange", "ContentBlockInlineStyleRange"]


class ContentBlockEntityRange(TypedDict, total=False):
    key: Required[int]

    length: Required[int]

    offset: Required[int]


class ContentBlockInlineStyleRange(TypedDict, total=False):
    length: Required[int]

    offset: Required[int]

    style: Required[str]


class ContentBlock(TypedDict, total=False):
    data: Required[Dict[str, object]]

    depth: Required[int]

    entity_ranges: Required[Annotated[Iterable[ContentBlockEntityRange], PropertyInfo(alias="entityRanges")]]

    inline_style_ranges: Required[
        Annotated[Iterable[ContentBlockInlineStyleRange], PropertyInfo(alias="inlineStyleRanges")]
    ]

    key: Required[str]

    text: Required[str]

    type: Required[str]


class Content(TypedDict, total=False):
    blocks: Required[Iterable[ContentBlock]]

    entity_map: Required[Annotated[Dict[str, object], PropertyInfo(alias="entityMap")]]


class DraftjsParam(TypedDict, total=False):
    content: Required[Content]
