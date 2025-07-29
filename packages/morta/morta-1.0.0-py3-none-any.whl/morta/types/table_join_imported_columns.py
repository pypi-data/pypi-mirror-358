# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TableJoinImportedColumns"]


class TableJoinImportedColumns(BaseModel):
    source_column_id: Optional[str] = FieldInfo(alias="sourceColumnId", default=None)

    target_column_id: Optional[str] = FieldInfo(alias="targetColumnId", default=None)
