# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ApikeyUpdateResponse"]


class ApikeyUpdateResponse(BaseModel):
    api_key: Optional[str] = FieldInfo(alias="apiKey", default=None)
    """Updated API key details"""
