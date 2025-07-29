# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .hub_secret import HubSecret

__all__ = ["SecretListResponse"]


class SecretListResponse(BaseModel):
    data: Optional[List[HubSecret]] = None

    metadata: Optional[object] = None
