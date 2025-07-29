# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .table_join import TableJoin

__all__ = ["TableListJoinsResponse"]


class TableListJoinsResponse(BaseModel):
    data: Optional[List[TableJoin]] = None

    metadata: Optional[Dict[str, object]] = None
