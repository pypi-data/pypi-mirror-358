# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["HubGetTagsResponse", "Data", "DataCell", "DataCellColumn"]


class DataCellColumn(BaseModel):
    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)


class DataCell(BaseModel):
    id: Optional[str] = None

    column: Optional[DataCellColumn] = None

    value: Optional[str] = None


class Data(BaseModel):
    cells: Optional[List[DataCell]] = None

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)


class HubGetTagsResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None
