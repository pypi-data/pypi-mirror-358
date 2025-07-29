# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import TypedDict

__all__ = ["TableGetStatisticsParams"]


class TableGetStatisticsParams(TypedDict, total=False):
    aggregation: Dict[str, str]
    """Aggregation functions to apply on columns"""

    filter: str
    """Filter criteria for the columns"""
