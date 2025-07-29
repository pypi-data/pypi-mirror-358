# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel
from .table_view import TableView

__all__ = ["ViewListResponse"]


class ViewListResponse(BaseModel):
    data: Optional[List[TableView]] = None

    metadata: Optional[Dict[str, object]] = None
