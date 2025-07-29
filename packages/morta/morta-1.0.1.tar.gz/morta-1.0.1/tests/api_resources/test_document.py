# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from morta import Morta, AsyncMorta
from morta.types import (
    DocumentCreateResponse,
    DocumentDeleteResponse,
    DocumentUpdateResponse,
    DocumentRestoreResponse,
    DocumentRetrieveResponse,
    DocumentSyncTemplateResponse,
    DocumentCreateSectionsResponse,
    DocumentGetDeletedSectionsResponse,
    DocumentUpdateSectionOrderResponse,
    DocumentGetDuplicatedChildrenResponse,
    DocumentCreateMultipleSectionsResponse,
    DocumentUpdateMultipleSectionsResponse,
    DocumentUpdateViewsPermissionsResponse,
)
from tests.utils import assert_matches_type
from morta._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocument:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        document = client.document.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        document = client.document.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.document.with_raw_response.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.document.with_streaming_response.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentCreateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        document = client.document.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Morta) -> None:
        document = client.document.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            exclude_children=True,
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.document.with_raw_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.document.with_streaming_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.retrieve(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        document = client.document.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        document = client.document.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            allow_comments=True,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            description={
                "content": {
                    "blocks": [
                        {
                            "data": {"foo": "bar"},
                            "depth": 0,
                            "entity_ranges": [
                                {
                                    "key": 0,
                                    "length": 0,
                                    "offset": 0,
                                }
                            ],
                            "inline_style_ranges": [
                                {
                                    "length": 0,
                                    "offset": 0,
                                    "style": "style",
                                }
                            ],
                            "key": "key",
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "entity_map": {"foo": "bar"},
                }
            },
            expand_by_default=True,
            is_template=True,
            locked_template=True,
            logo="logo",
            name="name",
            plaintext_description="plaintextDescription",
            type="type",
            variables=["string"],
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.document.with_raw_response.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.document.with_streaming_response.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentUpdateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.update(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        document = client.document.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.document.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.document.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentDeleteResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_multiple_sections(self, client: Morta) -> None:
        document = client.document.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"name": "name"}],
        )
        assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_multiple_sections_with_all_params(self, client: Morta) -> None:
        document = client.document.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[
                {
                    "name": "name",
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "parent_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "plaintext_description": "plaintextDescription",
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_multiple_sections(self, client: Morta) -> None:
        response = client.document.with_raw_response.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"name": "name"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_multiple_sections(self, client: Morta) -> None:
        with client.document.with_streaming_response.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"name": "name"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create_multiple_sections(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.create_multiple_sections(
                document_id="",
                sections=[{"name": "name"}],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_create_sections(self, client: Morta) -> None:
        document = client.document.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_sections_with_all_params(self, client: Morta) -> None:
        document = client.document.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            details=[
                {
                    "name": "name",
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "parent_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "plaintext_description": "plaintextDescription",
                }
            ],
        )
        assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_sections(self, client: Morta) -> None:
        response = client.document.with_raw_response.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_sections(self, client: Morta) -> None:
        with client.document.with_streaming_response.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create_sections(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.create_sections(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_export(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        document = client.document.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document.is_closed
        assert document.json() == {"foo": "bar"}
        assert cast(Any, document.is_closed) is True
        assert isinstance(document, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_export_with_all_params(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        document = client.document.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page_format="A1",
            page_orientation="portrait",
            table_links=True,
        )
        assert document.is_closed
        assert document.json() == {"foo": "bar"}
        assert cast(Any, document.is_closed) is True
        assert isinstance(document, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_export(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        document = client.document.with_raw_response.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert document.is_closed is True
        assert document.http_request.headers.get("X-Stainless-Lang") == "python"
        assert document.json() == {"foo": "bar"}
        assert isinstance(document, BinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_export(self, client: Morta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.document.with_streaming_response.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as document:
            assert not document.is_closed
            assert document.http_request.headers.get("X-Stainless-Lang") == "python"

            assert document.json() == {"foo": "bar"}
            assert cast(Any, document.is_closed) is True
            assert isinstance(document, StreamedBinaryAPIResponse)

        assert cast(Any, document.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_export(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.export(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_deleted_sections(self, client: Morta) -> None:
        document = client.document.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_deleted_sections_with_all_params(self, client: Morta) -> None:
        document = client.document.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            process_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_deleted_sections(self, client: Morta) -> None:
        response = client.document.with_raw_response.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_deleted_sections(self, client: Morta) -> None:
        with client.document.with_streaming_response.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_deleted_sections(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.get_deleted_sections(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_duplicated_children(self, client: Morta) -> None:
        document = client.document.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetDuplicatedChildrenResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_duplicated_children(self, client: Morta) -> None:
        response = client.document.with_raw_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGetDuplicatedChildrenResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_duplicated_children(self, client: Morta) -> None:
        with client.document.with_streaming_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGetDuplicatedChildrenResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_duplicated_children(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.get_duplicated_children(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_restore(self, client: Morta) -> None:
        document = client.document.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentRestoreResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_restore(self, client: Morta) -> None:
        response = client.document.with_raw_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentRestoreResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_restore(self, client: Morta) -> None:
        with client.document.with_streaming_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentRestoreResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_restore(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.restore(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_sync_template(self, client: Morta) -> None:
        document = client.document.sync_template(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentSyncTemplateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_sync_template(self, client: Morta) -> None:
        response = client.document.with_raw_response.sync_template(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentSyncTemplateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_sync_template(self, client: Morta) -> None:
        with client.document.with_streaming_response.sync_template(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentSyncTemplateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_sync_template(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.sync_template(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_multiple_sections(self, client: Morta) -> None:
        document = client.document.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )
        assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_multiple_sections_with_all_params(self, client: Morta) -> None:
        document = client.document.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "name": "name",
                    "page_break_before": True,
                    "pdf_include_description": True,
                    "pdf_include_section": True,
                    "plaintext_description": "plaintextDescription",
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_multiple_sections(self, client: Morta) -> None:
        response = client.document.with_raw_response.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_multiple_sections(self, client: Morta) -> None:
        with client.document.with_streaming_response.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_multiple_sections(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.update_multiple_sections(
                document_id="",
                sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_section_order(self, client: Morta) -> None:
        document = client.document.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_section_order_with_all_params(self, client: Morta) -> None:
        document = client.document.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            process_sections=[
                {
                    "parent_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "position": 0,
                    "section_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
        )
        assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_section_order(self, client: Morta) -> None:
        response = client.document.with_raw_response.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_section_order(self, client: Morta) -> None:
        with client.document.with_streaming_response.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update_section_order(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.with_raw_response.update_section_order(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update_views_permissions(self, client: Morta) -> None:
        document = client.document.update_views_permissions(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentUpdateViewsPermissionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update_views_permissions(self, client: Morta) -> None:
        response = client.document.with_raw_response.update_views_permissions(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentUpdateViewsPermissionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update_views_permissions(self, client: Morta) -> None:
        with client.document.with_streaming_response.update_views_permissions(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentUpdateViewsPermissionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDocument:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.create(
            name="name",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            type="type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentCreateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            exclude_children=True,
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.retrieve(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.retrieve(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            allow_comments=True,
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            description={
                "content": {
                    "blocks": [
                        {
                            "data": {"foo": "bar"},
                            "depth": 0,
                            "entity_ranges": [
                                {
                                    "key": 0,
                                    "length": 0,
                                    "offset": 0,
                                }
                            ],
                            "inline_style_ranges": [
                                {
                                    "length": 0,
                                    "offset": 0,
                                    "style": "style",
                                }
                            ],
                            "key": "key",
                            "text": "text",
                            "type": "type",
                        }
                    ],
                    "entity_map": {"foo": "bar"},
                }
            },
            expand_by_default=True,
            is_template=True,
            locked_template=True,
            logo="logo",
            name="name",
            plaintext_description="plaintextDescription",
            type="type",
            variables=["string"],
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.update(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentUpdateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.update(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentDeleteResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_multiple_sections(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"name": "name"}],
        )
        assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_multiple_sections_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[
                {
                    "name": "name",
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "parent_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "plaintext_description": "plaintextDescription",
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_multiple_sections(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"name": "name"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_multiple_sections(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.create_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"name": "name"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentCreateMultipleSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create_multiple_sections(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.create_multiple_sections(
                document_id="",
                sections=[{"name": "name"}],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_sections(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_sections_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            details=[
                {
                    "name": "name",
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "parent_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "plaintext_description": "plaintextDescription",
                }
            ],
        )
        assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_sections(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_sections(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.create_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentCreateSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create_sections(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.create_sections(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_export(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        document = await async_client.document.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document.is_closed
        assert await document.json() == {"foo": "bar"}
        assert cast(Any, document.is_closed) is True
        assert isinstance(document, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_export_with_all_params(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        document = await async_client.document.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            page_format="A1",
            page_orientation="portrait",
            table_links=True,
        )
        assert document.is_closed
        assert await document.json() == {"foo": "bar"}
        assert cast(Any, document.is_closed) is True
        assert isinstance(document, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_export(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        document = await async_client.document.with_raw_response.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert document.is_closed is True
        assert document.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await document.json() == {"foo": "bar"}
        assert isinstance(document, AsyncBinaryAPIResponse)

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_export(self, async_client: AsyncMorta, respx_mock: MockRouter) -> None:
        respx_mock.get("/v1/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/export").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.document.with_streaming_response.export(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as document:
            assert not document.is_closed
            assert document.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await document.json() == {"foo": "bar"}
            assert cast(Any, document.is_closed) is True
            assert isinstance(document, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, document.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_export(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.export(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_deleted_sections(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_deleted_sections_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            process_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_deleted_sections(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_deleted_sections(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.get_deleted_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGetDeletedSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_deleted_sections(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.get_deleted_sections(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetDuplicatedChildrenResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGetDuplicatedChildrenResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.get_duplicated_children(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGetDuplicatedChildrenResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_duplicated_children(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.get_duplicated_children(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_restore(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentRestoreResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentRestoreResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.restore(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentRestoreResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.restore(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_sync_template(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.sync_template(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentSyncTemplateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_sync_template(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.sync_template(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentSyncTemplateResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_sync_template(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.sync_template(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentSyncTemplateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_sync_template(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.sync_template(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_multiple_sections(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )
        assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_multiple_sections_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[
                {
                    "public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "context": {
                        "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                        "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    },
                    "description": {
                        "content": {
                            "blocks": [
                                {
                                    "data": {"foo": "bar"},
                                    "depth": 0,
                                    "entity_ranges": [
                                        {
                                            "key": 0,
                                            "length": 0,
                                            "offset": 0,
                                        }
                                    ],
                                    "inline_style_ranges": [
                                        {
                                            "length": 0,
                                            "offset": 0,
                                            "style": "style",
                                        }
                                    ],
                                    "key": "key",
                                    "text": "text",
                                    "type": "type",
                                }
                            ],
                            "entity_map": {"foo": "bar"},
                        }
                    },
                    "name": "name",
                    "page_break_before": True,
                    "pdf_include_description": True,
                    "pdf_include_section": True,
                    "plaintext_description": "plaintextDescription",
                }
            ],
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
        )
        assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_multiple_sections(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_multiple_sections(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.update_multiple_sections(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentUpdateMultipleSectionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_multiple_sections(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.update_multiple_sections(
                document_id="",
                sections=[{"public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"}],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_section_order(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_section_order_with_all_params(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            process_sections=[
                {
                    "parent_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                    "position": 0,
                    "section_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                }
            ],
        )
        assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_section_order(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_section_order(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.update_section_order(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentUpdateSectionOrderResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update_section_order(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.with_raw_response.update_section_order(
                document_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_views_permissions(self, async_client: AsyncMorta) -> None:
        document = await async_client.document.update_views_permissions(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentUpdateViewsPermissionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update_views_permissions(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.with_raw_response.update_views_permissions(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentUpdateViewsPermissionsResponse, document, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update_views_permissions(self, async_client: AsyncMorta) -> None:
        async with async_client.document.with_streaming_response.update_views_permissions(
            resource_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentUpdateViewsPermissionsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True
