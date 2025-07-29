# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .comment_model import CommentModel

__all__ = ["CommentUpdateResponse", "Metadata"]


class Metadata(BaseModel):
    change: Optional[object] = None
    """Changes made to the comment"""

    event: Optional[str] = None
    """Event type for the operation"""

    resource_id: Optional[str] = FieldInfo(alias="resourceId", default=None)
    """UUID of the updated comment"""


class CommentUpdateResponse(BaseModel):
    data: Optional[CommentModel] = None

    metadata: Optional[Metadata] = None
