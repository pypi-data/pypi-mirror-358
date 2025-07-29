# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .table_join import TableJoin

__all__ = ["HubGetResourcesResponse", "Data", "DataProcess", "DataTable"]


class DataProcess(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    logo: Optional[str] = None

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    type: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class DataTable(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    default_view_id: Optional[str] = FieldInfo(alias="defaultViewId", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)

    joins: Optional[List[TableJoin]] = None

    logo: Optional[str] = None

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)

    type: Optional[str] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)


class Data(BaseModel):
    name: Optional[str] = None
    """Name of the resource"""

    process: Optional[DataProcess] = None
    """Details of the document, if the resource type is 'process'"""

    table: Optional[DataTable] = None
    """Details of the table, if the resource type is 'table'"""

    type: Optional[str] = None
    """Type of the resource (document or table)"""


class HubGetResourcesResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None
