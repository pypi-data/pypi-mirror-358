# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["HubListFavouritesResponse", "Data"]


class Data(BaseModel):
    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)
    """Indicates if the hub is deleted"""

    name: Optional[str] = None
    """Name of the hub"""

    project_role: Optional[str] = FieldInfo(alias="projectRole", default=None)
    """User's role in the hub"""

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)
    """Public ID of the hub"""


class HubListFavouritesResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None
    """Additional metadata"""
