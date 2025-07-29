# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["SelectOptionsLookup", "TableOptions", "TableOptionsDependency"]


class TableOptionsDependency(BaseModel):
    column_id: str = FieldInfo(alias="columnId")

    column_join_id: Optional[str] = FieldInfo(alias="columnJoinId", default=None)


class TableOptions(BaseModel):
    column_id: Optional[str] = FieldInfo(alias="columnId", default=None)

    dependencies: Optional[List[TableOptionsDependency]] = None

    live_values: Optional[bool] = FieldInfo(alias="liveValues", default=None)

    table_id: Optional[str] = FieldInfo(alias="tableId", default=None)

    view_id: Optional[str] = FieldInfo(alias="viewId", default=None)


class SelectOptionsLookup(BaseModel):
    autopopulate: Optional[bool] = None

    manual_options: Optional[List[str]] = FieldInfo(alias="manualOptions", default=None)

    table_options: Optional[TableOptions] = FieldInfo(alias="tableOptions", default=None)
