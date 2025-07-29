# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Group"]


class Group(BaseModel):
    column_name: str = FieldInfo(alias="columnName")

    direction: str

    column_id: Optional[str] = FieldInfo(alias="columnId", default=None)
