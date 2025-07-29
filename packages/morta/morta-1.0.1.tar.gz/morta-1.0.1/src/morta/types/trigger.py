# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Trigger"]


class Trigger(BaseModel):
    public_id: str = FieldInfo(alias="publicId")

    resource: str

    verb: str
