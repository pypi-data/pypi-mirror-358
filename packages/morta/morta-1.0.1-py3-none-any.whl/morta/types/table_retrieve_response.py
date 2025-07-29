# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .table.table import Table

__all__ = ["TableRetrieveResponse", "Metadata"]


class Metadata(BaseModel):
    page: Optional[int] = None
    """Current page number"""

    size: Optional[int] = None
    """Number of items per page"""

    total: Optional[int] = None
    """Total number of rows in the table"""


class TableRetrieveResponse(BaseModel):
    data: Optional[Table] = None

    metadata: Optional[Metadata] = None
