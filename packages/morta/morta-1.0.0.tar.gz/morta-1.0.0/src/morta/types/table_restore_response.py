# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .table.table import Table

__all__ = ["TableRestoreResponse"]


class TableRestoreResponse(BaseModel):
    data: Optional[Table] = None

    metadata: Optional[object] = None
