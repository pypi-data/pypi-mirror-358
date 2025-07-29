# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .table.table import Table

__all__ = ["HubGetTablesResponse"]


class HubGetTablesResponse(BaseModel):
    data: Optional[List[Table]] = None

    metadata: Optional[object] = None
