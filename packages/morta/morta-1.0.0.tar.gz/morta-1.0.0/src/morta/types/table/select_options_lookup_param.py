# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["SelectOptionsLookupParam", "TableOptions", "TableOptionsDependency"]


class TableOptionsDependency(TypedDict, total=False):
    column_id: Required[Annotated[str, PropertyInfo(alias="columnId")]]

    column_join_id: Annotated[Optional[str], PropertyInfo(alias="columnJoinId")]


class TableOptions(TypedDict, total=False):
    column_id: Annotated[str, PropertyInfo(alias="columnId")]

    dependencies: Optional[Iterable[TableOptionsDependency]]

    live_values: Annotated[bool, PropertyInfo(alias="liveValues")]

    table_id: Annotated[str, PropertyInfo(alias="tableId")]

    view_id: Annotated[str, PropertyInfo(alias="viewId")]


class SelectOptionsLookupParam(TypedDict, total=False):
    autopopulate: bool

    manual_options: Annotated[List[str], PropertyInfo(alias="manualOptions")]

    table_options: Annotated[TableOptions, PropertyInfo(alias="tableOptions")]
