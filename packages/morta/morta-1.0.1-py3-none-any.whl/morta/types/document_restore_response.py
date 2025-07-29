# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

from .._compat import PYDANTIC_V2
from .._models import BaseModel

__all__ = ["DocumentRestoreResponse"]


class DocumentRestoreResponse(BaseModel):
    data: Optional["MortaDocument"] = None

    metadata: Optional[object] = None


from .morta_document import MortaDocument

if PYDANTIC_V2:
    DocumentRestoreResponse.model_rebuild()
else:
    DocumentRestoreResponse.update_forward_refs()  # type: ignore
