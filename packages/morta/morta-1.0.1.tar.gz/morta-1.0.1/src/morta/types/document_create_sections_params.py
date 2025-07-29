# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import TypedDict

from .base_request_context_param import BaseRequestContextParam
from .document.create_document_section_param import CreateDocumentSectionParam

__all__ = ["DocumentCreateSectionsParams"]


class DocumentCreateSectionsParams(TypedDict, total=False):
    context: BaseRequestContextParam

    details: Iterable[CreateDocumentSectionParam]
