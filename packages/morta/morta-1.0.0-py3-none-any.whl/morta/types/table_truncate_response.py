# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel

__all__ = ["TableTruncateResponse"]


class TableTruncateResponse(BaseModel):
    data: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
