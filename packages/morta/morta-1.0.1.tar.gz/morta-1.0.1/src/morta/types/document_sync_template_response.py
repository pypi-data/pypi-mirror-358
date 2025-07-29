# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .document.document import Document

__all__ = ["DocumentSyncTemplateResponse"]


class DocumentSyncTemplateResponse(BaseModel):
    data: Optional[List[Document]] = None

    metadata: Optional[object] = None
