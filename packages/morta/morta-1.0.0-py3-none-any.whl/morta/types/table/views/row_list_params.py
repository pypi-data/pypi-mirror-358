# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RowListParams"]


class RowListParams(TypedDict, total=False):
    alphabetical_column_sort: Annotated[bool, PropertyInfo(alias="alphabeticalColumnSort")]
    """
    If true, columns in row data are sorted alphabetically otherwise columns in row
    data follows their order in the view.
    """

    filter: str
    """URL encoded JSON string of filter criteria (e.g.

    'filter=%7B%22columnName%22%3A%22Price%22%2C%22value%22%3A%22100%22%2C%22filterType%22%3A%22gt%22%7D')
    """

    page: int
    """Page number for pagination."""

    size: int
    """Number of items per page for pagination."""

    sort: str
    """
    Sort the results by a field, this parameter takes the form
    `ColumnName:SortDirection`, for example to sort by price ascending
    `sort=Price:asc`. Sort direction can be either `asc` or `desc`. You can pass
    multiple sort parameters to add secondary and tertiary sorts etc., the sort will
    be applied in the order of the query string.
    """
