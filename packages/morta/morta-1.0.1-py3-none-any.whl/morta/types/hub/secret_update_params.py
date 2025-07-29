# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SecretUpdateParams"]


class SecretUpdateParams(TypedDict, total=False):
    hub_id: Required[str]

    name: Required[str]

    value: Required[str]
