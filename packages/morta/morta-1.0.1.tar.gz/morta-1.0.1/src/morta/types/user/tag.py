# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Tag"]


class Tag(BaseModel):
    document_table_id: Optional[str] = FieldInfo(alias="documentTableId", default=None)

    project_public_id: Optional[str] = FieldInfo(alias="projectPublicId", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    reference_public_id: Optional[str] = FieldInfo(alias="referencePublicId", default=None)

    value: Optional[object] = None
