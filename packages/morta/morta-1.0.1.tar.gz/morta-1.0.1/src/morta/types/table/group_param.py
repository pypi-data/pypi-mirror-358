# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["GroupParam"]


class GroupParam(TypedDict, total=False):
    column_name: Required[Annotated[str, PropertyInfo(alias="columnName")]]

    direction: Required[str]

    column_id: Annotated[str, PropertyInfo(alias="columnId")]
