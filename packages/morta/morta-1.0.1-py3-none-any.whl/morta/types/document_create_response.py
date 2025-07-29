# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .document.document import Document

__all__ = ["DocumentCreateResponse", "Metadata"]


class Metadata(BaseModel):
    change: Optional[object] = None
    """The changes made during document creation"""

    event: Optional[str] = None
    """The event type, e.g., 'process.created'"""

    resource_id: Optional[str] = FieldInfo(alias="resourceId", default=None)
    """The UUID of the newly created document"""


class DocumentCreateResponse(BaseModel):
    data: Optional[Document] = None

    metadata: Optional[Metadata] = None
