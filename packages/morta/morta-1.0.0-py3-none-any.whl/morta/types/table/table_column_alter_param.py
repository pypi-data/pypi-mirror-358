# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TableColumnAlterParam"]


class TableColumnAlterParam(TypedDict, total=False):
    date_conversion_format: Annotated[
        Literal["DD/MM/YYYY", "MM/DD/YYYY", "ISO8601", "DD-Mon-YY"], PropertyInfo(alias="dateConversionFormat")
    ]

    run_script_on_all_cells: Annotated[bool, PropertyInfo(alias="runScriptOnAllCells")]
