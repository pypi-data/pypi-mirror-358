# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["UserListContributionsResponse"]


class UserListContributionsResponse(BaseModel):
    data: Optional[Dict[str, int]] = None
    """Contributions per day, keyed by date"""

    metadata: Optional[object] = None
    """Metadata object"""
