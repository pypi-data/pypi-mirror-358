# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DocumentCreateMultipleSectionsResponse", "Metadata"]


class Metadata(BaseModel):
    resource_ids: Optional[List[str]] = FieldInfo(alias="resourceIds", default=None)
    """List of UUIDs for the newly created document sections"""


class DocumentCreateMultipleSectionsResponse(BaseModel):
    data: Optional[str] = None

    metadata: Optional[Metadata] = None
