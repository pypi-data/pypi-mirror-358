# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["TableColumnAlter"]


class TableColumnAlter(BaseModel):
    date_conversion_format: Optional[Literal["DD/MM/YYYY", "MM/DD/YYYY", "ISO8601", "DD-Mon-YY"]] = FieldInfo(
        alias="dateConversionFormat", default=None
    )

    run_script_on_all_cells: Optional[bool] = FieldInfo(alias="runScriptOnAllCells", default=None)
