# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional

from ...._compat import PYDANTIC_V2
from ...._models import BaseModel

__all__ = ["ResponseSubmitResponse"]


class ResponseSubmitResponse(BaseModel):
    data: Optional["MortaDocumentSection"] = None

    metadata: Optional[Dict[str, object]] = None


from ...morta_document_section import MortaDocumentSection

if PYDANTIC_V2:
    ResponseSubmitResponse.model_rebuild()
else:
    ResponseSubmitResponse.update_forward_refs()  # type: ignore
