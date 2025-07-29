# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel
from .table_view import TableView

__all__ = ["ViewUpdateResponse"]


class ViewUpdateResponse(BaseModel):
    data: Optional[TableView] = None

    metadata: Optional[Dict[str, object]] = None
