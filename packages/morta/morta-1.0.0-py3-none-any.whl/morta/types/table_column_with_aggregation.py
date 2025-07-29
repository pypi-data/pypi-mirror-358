# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["TableColumnWithAggregation", "Aggregation"]


class Aggregation(BaseModel):
    name: Optional[str] = None

    value: Optional[float] = None


class TableColumnWithAggregation(BaseModel):
    aggregation: Optional[Aggregation] = None

    name: Optional[str] = None

    public_id: Optional[str] = FieldInfo(alias="publicId", default=None)
