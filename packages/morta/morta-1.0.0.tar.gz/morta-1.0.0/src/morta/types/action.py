# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Action", "CustomHeader"]


class CustomHeader(BaseModel):
    key: str

    value: str


class Action(BaseModel):
    kind: str

    public_id: str = FieldInfo(alias="publicId")

    custom_headers: Optional[List[CustomHeader]] = FieldInfo(alias="customHeaders", default=None)

    webhook_url: Optional[str] = FieldInfo(alias="webhookUrl", default=None)
