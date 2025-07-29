# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .table3 import Table3
from .project import Project
from .._models import BaseModel
from .user.tag import Tag
from .document.document import Document

__all__ = ["AccessPolicy", "AccessAttribute", "AccessAttributeUser", "AccessResource"]


class AccessAttributeUser(BaseModel):
    firebase_user_id: Optional[str] = FieldInfo(alias="firebaseUserId", default=None)

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)


class AccessAttribute(BaseModel):
    document_table: Optional[Table3] = FieldInfo(alias="documentTable", default=None)

    kind: Optional[str] = None

    project: Optional[Project] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    tag: Optional[Tag] = None

    user: Optional[AccessAttributeUser] = None


class AccessResource(BaseModel):
    document_table: Optional[Table3] = FieldInfo(alias="documentTable", default=None)

    kind: Optional[str] = None

    process: Optional[Document] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)


class AccessPolicy(BaseModel):
    access_attribute: Optional[AccessAttribute] = FieldInfo(alias="accessAttribute", default=None)

    access_resource: Optional[AccessResource] = FieldInfo(alias="accessResource", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    role: Optional[int] = None

    role_label: Optional[str] = FieldInfo(alias="roleLabel", default=None)
