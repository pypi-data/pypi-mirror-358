# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["HubTogglePinResponse", "Data"]


class Data(BaseModel):
    contributors: Optional[int] = None
    """Number of contributors to the hub"""

    name: Optional[str] = None
    """Name of the hub"""

    primary_colour: Optional[str] = FieldInfo(alias="primaryColour", default=None)
    """Primary colour of the hub"""

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)
    """Public ID of the hub"""

    views: Optional[int] = None
    """Number of views of the hub"""


class HubTogglePinResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None
    """Additional metadata"""
