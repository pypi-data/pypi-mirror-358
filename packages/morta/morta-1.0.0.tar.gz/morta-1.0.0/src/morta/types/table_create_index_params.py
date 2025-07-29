# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TableCreateIndexParams", "Column"]


class TableCreateIndexParams(TypedDict, total=False):
    columns: Required[Iterable[Column]]


class Column(TypedDict, total=False):
    public_id: Required[Annotated[str, PropertyInfo(alias="publicId")]]
