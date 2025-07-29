# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

from ..._compat import PYDANTIC_V2
from ..._models import BaseModel

__all__ = ["SectionRetrieveResponse"]


class SectionRetrieveResponse(BaseModel):
    data: Optional["MortaDocumentSection"] = None

    metadata: Optional[object] = None


from ..morta_document_section import MortaDocumentSection

if PYDANTIC_V2:
    SectionRetrieveResponse.model_rebuild()
else:
    SectionRetrieveResponse.update_forward_refs()  # type: ignore
