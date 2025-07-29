# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel
from .table_view import TableView

__all__ = ["ViewDuplicateResponse"]


class ViewDuplicateResponse(BaseModel):
    data: Optional[TableView] = None

    metadata: Optional[Dict[str, object]] = None
