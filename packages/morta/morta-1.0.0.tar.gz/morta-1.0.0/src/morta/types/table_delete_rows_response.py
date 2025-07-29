# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["TableDeleteRowsResponse"]


class TableDeleteRowsResponse(BaseModel):
    data: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
