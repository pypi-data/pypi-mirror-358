# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ...._models import BaseModel

__all__ = ["ColumnAIFormulaHelperResponse", "Data"]


class Data(BaseModel):
    ai_formula_helper: Optional[Dict[str, object]] = None


class ColumnAIFormulaHelperResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[Dict[str, object]] = None
