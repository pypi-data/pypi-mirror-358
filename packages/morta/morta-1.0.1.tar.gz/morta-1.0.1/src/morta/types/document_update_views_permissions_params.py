# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DocumentUpdateViewsPermissionsParams"]


class DocumentUpdateViewsPermissionsParams(TypedDict, total=False):
    resource_id: Required[str]
    """UUID of the document for which to retrieve permissions."""
