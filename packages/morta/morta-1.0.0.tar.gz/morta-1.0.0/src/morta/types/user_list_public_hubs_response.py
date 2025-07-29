# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .user.home_hub import HomeHub

__all__ = ["UserListPublicHubsResponse"]


class UserListPublicHubsResponse(BaseModel):
    data: Optional[List[HomeHub]] = None

    metadata: Optional[object] = None
    """Additional metadata"""
