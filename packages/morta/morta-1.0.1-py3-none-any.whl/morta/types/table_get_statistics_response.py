# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .table_column_with_aggregation import TableColumnWithAggregation

__all__ = ["TableGetStatisticsResponse"]


class TableGetStatisticsResponse(BaseModel):
    data: Optional[List[TableColumnWithAggregation]] = None

    metadata: Optional[object] = None
