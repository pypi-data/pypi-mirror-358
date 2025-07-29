# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .tag import Tag
from ..._models import BaseModel

__all__ = ["TagBulkApplyResponse"]


class TagBulkApplyResponse(BaseModel):
    data: Optional[List[Tag]] = None

    metadata: Optional[object] = None
    """Additional metadata"""
