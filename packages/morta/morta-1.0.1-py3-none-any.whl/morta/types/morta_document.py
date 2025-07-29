# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._compat import PYDANTIC_V2
from .._models import BaseModel

__all__ = ["MortaDocument"]


class MortaDocument(BaseModel):
    allow_comments: Optional[bool] = FieldInfo(alias="allowComments", default=None)

    children: Optional[List["DocumentSection1"]] = None

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    description: Optional[object] = None

    expand_by_default: Optional[bool] = FieldInfo(alias="expandByDefault", default=None)

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    is_template: Optional[bool] = FieldInfo(alias="isTemplate", default=None)

    locked_template: Optional[bool] = FieldInfo(alias="lockedTemplate", default=None)

    logo: Optional[str] = None

    name: Optional[str] = None

    project_name: Optional[str] = FieldInfo(alias="projectName", default=None)

    project_public_id: Optional[str] = FieldInfo(alias="projectPublicId", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    type: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)

    variables: Optional[List[str]] = None

    variable_values: Optional[List[str]] = FieldInfo(alias="variableValues", default=None)


from .document_section_1 import DocumentSection1

if PYDANTIC_V2:
    MortaDocument.model_rebuild()
else:
    MortaDocument.update_forward_refs()  # type: ignore
