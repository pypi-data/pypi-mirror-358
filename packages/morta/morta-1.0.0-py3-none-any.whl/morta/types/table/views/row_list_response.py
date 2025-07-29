# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RowListResponse", "Data", "Metadata"]


class Data(BaseModel):
    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    row_data: Optional[Dict[str, object]] = FieldInfo(alias="rowData", default=None)

    sort_order: Optional[float] = FieldInfo(alias="sortOrder", default=None)


class Metadata(BaseModel):
    next_page_token: Optional[str] = None

    size: Optional[int] = None

    total: Optional[int] = None


class RowListResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[Metadata] = None
