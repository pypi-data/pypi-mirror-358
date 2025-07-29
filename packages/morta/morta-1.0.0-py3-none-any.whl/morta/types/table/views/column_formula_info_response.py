# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ...._models import BaseModel

__all__ = ["ColumnFormulaInfoResponse", "Data"]


class Data(BaseModel):
    formula_info: Optional[Dict[str, object]] = None


class ColumnFormulaInfoResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[Dict[str, object]] = None
