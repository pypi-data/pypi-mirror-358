# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .table_column import TableColumn

__all__ = ["ColumnUpdateResponse"]


class ColumnUpdateResponse(BaseModel):
    data: Optional[TableColumn] = None

    metadata: Optional[object] = None
