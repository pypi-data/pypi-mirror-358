# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .api_key import APIKey
from ..._models import BaseModel

__all__ = ["ApikeyCreateResponse"]


class ApikeyCreateResponse(BaseModel):
    data: Optional[APIKey] = None

    metadata: Optional[object] = None
