# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional

from ...._compat import PYDANTIC_V2
from ...._models import BaseModel

__all__ = ["ResponseResetResponse"]


class ResponseResetResponse(BaseModel):
    data: Optional["MortaDocumentSection"] = None

    metadata: Optional[Dict[str, object]] = None


from ...morta_document_section import MortaDocumentSection

if PYDANTIC_V2:
    ResponseResetResponse.model_rebuild()
else:
    ResponseResetResponse.update_forward_refs()  # type: ignore
