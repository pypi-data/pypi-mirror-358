# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .home_hub import HomeHub
from ..._models import BaseModel

__all__ = ["HubListResponse"]


class HubListResponse(BaseModel):
    data: Optional[List[HomeHub]] = None

    metadata: Optional[object] = None
    """Additional metadata"""
