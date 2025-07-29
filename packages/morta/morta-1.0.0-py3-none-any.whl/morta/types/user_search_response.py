# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .summary_user import SummaryUser

__all__ = ["UserSearchResponse"]


class UserSearchResponse(BaseModel):
    data: Optional[List[SummaryUser]] = None

    metadata: Optional[object] = None
    """Additional metadata"""
