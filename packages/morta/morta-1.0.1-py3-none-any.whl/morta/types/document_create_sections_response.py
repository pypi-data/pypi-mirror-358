# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

from .._compat import PYDANTIC_V2
from .._models import BaseModel

__all__ = ["DocumentCreateSectionsResponse"]


class DocumentCreateSectionsResponse(BaseModel):
    data: Optional[List["MortaDocumentSection"]] = None

    metadata: Optional[object] = None


from .morta_document_section import MortaDocumentSection

if PYDANTIC_V2:
    DocumentCreateSectionsResponse.model_rebuild()
else:
    DocumentCreateSectionsResponse.update_forward_refs()  # type: ignore
