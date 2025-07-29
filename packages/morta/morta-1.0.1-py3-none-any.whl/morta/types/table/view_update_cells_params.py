# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["ViewUpdateCellsParams", "Cell"]


class ViewUpdateCellsParams(TypedDict, total=False):
    cells: Required[Iterable[Cell]]

    context: BaseRequestContextParam


class Cell(TypedDict, total=False):
    column_name: Required[Annotated[str, PropertyInfo(alias="columnName")]]

    row_id: Required[Annotated[str, PropertyInfo(alias="rowId")]]

    value: Required[object]

    context: BaseRequestContextParam
