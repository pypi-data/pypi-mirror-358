# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PermissionRetrieveTagParams"]


class PermissionRetrieveTagParams(TypedDict, total=False):
    tag_id: Required[str]
    """Public ID of the tag to retrieve."""
