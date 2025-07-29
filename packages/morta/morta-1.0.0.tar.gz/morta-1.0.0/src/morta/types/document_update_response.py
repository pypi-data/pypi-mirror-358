# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .simple_document import SimpleDocument

__all__ = ["DocumentUpdateResponse"]


class DocumentUpdateResponse(BaseModel):
    data: Optional[SimpleDocument] = None

    metadata: Optional[object] = None
