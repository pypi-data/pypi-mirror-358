# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .event import Event
from .._models import BaseModel

__all__ = ["UserListPublicContributionsResponse"]


class UserListPublicContributionsResponse(BaseModel):
    data: Optional[List[Event]] = None

    metadata: Optional[object] = None
    """Metadata object"""
