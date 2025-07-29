# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .simple_document import SimpleDocument

__all__ = ["HubGetDocumentsResponse"]


class HubGetDocumentsResponse(BaseModel):
    data: Optional[List[SimpleDocument]] = None

    metadata: Optional[object] = None
