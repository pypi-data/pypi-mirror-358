# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .table.table_column import TableColumn

__all__ = ["TableListColumnsResponse"]


class TableListColumnsResponse(BaseModel):
    data: Optional[List[TableColumn]] = None

    metadata: Optional[object] = None
