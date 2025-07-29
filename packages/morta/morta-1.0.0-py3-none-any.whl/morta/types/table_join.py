# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .table.table_column_join import TableColumnJoin
from .table_join_imported_columns import TableJoinImportedColumns

__all__ = ["TableJoin"]


class TableJoin(BaseModel):
    data_columns: Optional[List[TableJoinImportedColumns]] = FieldInfo(alias="dataColumns", default=None)

    is_one_to_many: Optional[bool] = FieldInfo(alias="isOneToMany", default=None)

    join_columns: Optional[List[TableColumnJoin]] = FieldInfo(alias="joinColumns", default=None)

    join_table_id: Optional[str] = FieldInfo(alias="joinTableId", default=None)

    join_view_id: Optional[str] = FieldInfo(alias="joinViewId", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)
