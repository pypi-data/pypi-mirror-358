# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["ColumnGetDistinctValuesResponse"]


class ColumnGetDistinctValuesResponse(BaseModel):
    data: Optional[List[str]] = None

    metadata: Optional[Dict[str, object]] = None
