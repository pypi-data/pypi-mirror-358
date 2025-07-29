# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ColumnAIFormulaHelperParams"]


class ColumnAIFormulaHelperParams(TypedDict, total=False):
    view_id: Required[str]

    text: Required[str]
