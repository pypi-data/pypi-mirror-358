# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["TableCheckUsageResponse", "Data"]


class Data(BaseModel):
    link: Optional[str] = None
    """Direct link to the document, join or select"""

    name: Optional[str] = None
    """Name of the document, join or select where the table is used"""

    type: Optional[str] = None
    """Type of usage (process, sourceJoin, targetJoin, sourceSelect, etc.)"""


class TableCheckUsageResponse(BaseModel):
    data: Optional[List[Data]] = None

    metadata: Optional[object] = None
