# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .table import Table
from ..._models import BaseModel

__all__ = ["JoinCreateResponse"]


class JoinCreateResponse(BaseModel):
    data: Optional[Table] = None

    metadata: Optional[Dict[str, object]] = None
