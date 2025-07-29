# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel
from ..table_column_with_aggregation import TableColumnWithAggregation

__all__ = ["ViewStatsResponse"]


class ViewStatsResponse(BaseModel):
    data: Optional[List[TableColumnWithAggregation]] = None

    metadata: Optional[Dict[str, object]] = None
