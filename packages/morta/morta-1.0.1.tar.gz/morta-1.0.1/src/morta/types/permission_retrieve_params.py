# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["PermissionRetrieveParams"]


class PermissionRetrieveParams(TypedDict, total=False):
    resource: Required[Literal["process", "table", "table_view"]]
    """The kind of resource for which to retrieve permissions.

    Valid options are 'process', 'table', or 'table_view'.
    """

    resource_id: Required[str]
    """UUID of the resource for which to retrieve permissions."""
