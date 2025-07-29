# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .table.table_column import TableColumn

__all__ = ["TableCreateIndexResponse"]


class TableCreateIndexResponse(BaseModel):
    data: Optional[List[TableColumn]] = None

    metadata: Optional[Dict[str, object]] = None
