# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["IntegrationCreatePassthroughResponse", "Data"]


class Data(BaseModel):
    body: Optional[object] = None

    content_type: Optional[str] = FieldInfo(alias="contentType", default=None)

    headers: Optional[object] = None

    status: Optional[str] = None


class IntegrationCreatePassthroughResponse(BaseModel):
    data: Optional[Data] = None

    metadata: Optional[Dict[str, object]] = None
