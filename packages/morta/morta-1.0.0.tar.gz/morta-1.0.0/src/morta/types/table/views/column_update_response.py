# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ...._models import BaseModel
from .table_view_column import TableViewColumn

__all__ = ["ColumnUpdateResponse"]


class ColumnUpdateResponse(BaseModel):
    data: Optional[TableViewColumn] = None

    metadata: Optional[Dict[str, object]] = None
