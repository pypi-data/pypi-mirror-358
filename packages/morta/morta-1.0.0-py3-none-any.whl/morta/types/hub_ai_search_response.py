# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .answer import Answer
from .._models import BaseModel

__all__ = ["HubAISearchResponse"]


class HubAISearchResponse(BaseModel):
    data: Optional[Answer] = None

    metadata: Optional[object] = None
