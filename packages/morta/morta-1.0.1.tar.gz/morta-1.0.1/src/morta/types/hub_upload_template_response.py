# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .simple_hub import SimpleHub

__all__ = ["HubUploadTemplateResponse"]


class HubUploadTemplateResponse(BaseModel):
    data: Optional[SimpleHub] = None

    metadata: Optional[object] = None
