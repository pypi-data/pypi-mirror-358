# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..base_request_context_param import BaseRequestContextParam

__all__ = ["TableRowActionParam"]


class TableRowActionParam(TypedDict, total=False):
    row_data: Required[Annotated[Dict[str, Optional[object]], PropertyInfo(alias="rowData")]]

    context: BaseRequestContextParam

    sort_order: Annotated[float, PropertyInfo(alias="sortOrder")]
