# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ...._models import BaseModel
from .document_response import DocumentResponse

__all__ = ["ResponseRestoreResponse"]


class ResponseRestoreResponse(BaseModel):
    data: Optional[DocumentResponse] = None

    metadata: Optional[Dict[str, object]] = None
