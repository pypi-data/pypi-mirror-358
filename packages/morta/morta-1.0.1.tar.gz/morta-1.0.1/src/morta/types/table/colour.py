# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Colour"]


class Colour(BaseModel):
    background_colour: str = FieldInfo(alias="backgroundColour")

    column_name: str = FieldInfo(alias="columnName")

    filter_type: Literal[
        "eq",
        "lt",
        "gt",
        "lte",
        "gte",
        "neq",
        "contains",
        "in",
        "row_id",
        "is",
        "is_not",
        "one_of",
        "not_one_of",
        "is_null",
        "is_not_null",
        "not_contains",
        "starts_with",
        "ends_with",
        "is_valid",
        "is_not_valid",
    ] = FieldInfo(alias="filterType")

    font_colour: str = FieldInfo(alias="fontColour")

    column_id: Optional[str] = FieldInfo(alias="columnId", default=None)

    multiple_values: Optional[List[Optional[object]]] = FieldInfo(alias="multipleValues", default=None)

    value: Optional[object] = None
