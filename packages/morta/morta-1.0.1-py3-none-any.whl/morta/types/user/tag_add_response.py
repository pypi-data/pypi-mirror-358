# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .tag import Tag
from ..._models import BaseModel

__all__ = ["TagAddResponse"]


class TagAddResponse(BaseModel):
    data: Optional[Tag] = None

    metadata: Optional[object] = None
    """Additional metadata"""
