# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["APIKey"]


class APIKey(BaseModel):
    access_level: Optional[int] = FieldInfo(alias="accessLevel", default=None)

    document_restrictions: Optional[List[str]] = FieldInfo(alias="documentRestrictions", default=None)

    hash: Optional[str] = None

    name: Optional[str] = None

    prefix: Optional[str] = None

    project_restrictions: Optional[List[str]] = FieldInfo(alias="projectRestrictions", default=None)

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    table_restrictions: Optional[List[str]] = FieldInfo(alias="tableRestrictions", default=None)
