# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .document_response import DocumentResponse

__all__ = ["ResponseCreateResponse"]


class ResponseCreateResponse(BaseModel):
    data: Optional[DocumentResponse] = None

    metadata: Optional[object] = None
