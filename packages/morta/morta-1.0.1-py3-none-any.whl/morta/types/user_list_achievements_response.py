# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["UserListAchievementsResponse", "Data"]


class Data(BaseModel):
    created_processes: Optional[int] = FieldInfo(alias="createdProcesses", default=None)
    """Number of processes created by the user"""

    created_tables: Optional[int] = FieldInfo(alias="createdTables", default=None)
    """Number of tables created by the user"""


class UserListAchievementsResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[object] = None
    """Metadata object"""
