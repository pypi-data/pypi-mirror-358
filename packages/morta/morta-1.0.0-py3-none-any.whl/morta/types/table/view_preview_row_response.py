# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ViewPreviewRowResponse", "Data"]


class Data(BaseModel):
    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    row_data: Optional[Dict[str, str]] = FieldInfo(alias="rowData", default=None)

    sort_order: Optional[int] = FieldInfo(alias="sortOrder", default=None)


class ViewPreviewRowResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[Dict[str, object]] = None
