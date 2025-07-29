# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.document import (
    SectionCreateResponse,
    SectionDeleteResponse,
    SectionUpdateResponse,
    SectionRestoreResponse,
    SectionRetrieveResponse,
    SectionDuplicateResponse,
    SectionDuplicateAsyncResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSection:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        section = client.document.section.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(SectionCreateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        section = client.document.section.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
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
            parent_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaintext_description="plaintextDescription",
        )
        assert_matches_type(SectionCreateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionCreateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionCreateResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_create(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.create(
                document_id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        section = client.document.section.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionRetrieveResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Morta) -> None:
        section = client.document.section.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            main_parent_section=True,
        )
        assert_matches_type(SectionRetrieveResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionRetrieveResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionRetrieveResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.retrieve(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.with_raw_response.retrieve(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Morta) -> None:
        section = client.document.section.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionUpdateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Morta) -> None:
        section = client.document.section.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
            name="name",
            page_break_before=True,
            pdf_include_description=True,
            pdf_include_section=True,
            plaintext_description="plaintextDescription",
        )
        assert_matches_type(SectionUpdateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionUpdateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionUpdateResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.update(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.with_raw_response.update(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        section = client.document.section.delete(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionDeleteResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.delete(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionDeleteResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.delete(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionDeleteResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.delete(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.with_raw_response.delete(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate(self, client: Morta) -> None:
        section = client.document.section.duplicate(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionDuplicateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.duplicate(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionDuplicateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.duplicate(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionDuplicateResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.duplicate(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.with_raw_response.duplicate(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate_async(self, client: Morta) -> None:
        section = client.document.section.duplicate_async(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionDuplicateAsyncResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate_async(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.duplicate_async(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionDuplicateAsyncResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate_async(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.duplicate_async(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionDuplicateAsyncResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate_async(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.duplicate_async(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.with_raw_response.duplicate_async(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_restore(self, client: Morta) -> None:
        section = client.document.section.restore(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionRestoreResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_restore(self, client: Morta) -> None:
        response = client.document.section.with_raw_response.restore(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = response.parse()
        assert_matches_type(SectionRestoreResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_restore(self, client: Morta) -> None:
        with client.document.section.with_streaming_response.restore(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = response.parse()
            assert_matches_type(SectionRestoreResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_restore(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.section.with_raw_response.restore(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            client.document.section.with_raw_response.restore(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncSection:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )
        assert_matches_type(SectionCreateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
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
            parent_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaintext_description="plaintextDescription",
        )
        assert_matches_type(SectionCreateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionCreateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.create(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionCreateResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_create(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.create(
                document_id="",
                name="name",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionRetrieveResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            main_parent_section=True,
        )
        assert_matches_type(SectionRetrieveResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionRetrieveResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.retrieve(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionRetrieveResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.retrieve(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.with_raw_response.retrieve(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionUpdateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
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
            name="name",
            page_break_before=True,
            pdf_include_description=True,
            pdf_include_section=True,
            plaintext_description="plaintextDescription",
        )
        assert_matches_type(SectionUpdateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionUpdateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.update(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionUpdateResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.update(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.with_raw_response.update(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.delete(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionDeleteResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.delete(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionDeleteResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.delete(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionDeleteResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.delete(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.with_raw_response.delete(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.duplicate(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionDuplicateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.duplicate(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionDuplicateResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.duplicate(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionDuplicateResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.duplicate(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.with_raw_response.duplicate(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate_async(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.duplicate_async(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionDuplicateAsyncResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate_async(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.duplicate_async(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionDuplicateAsyncResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate_async(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.duplicate_async(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionDuplicateAsyncResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate_async(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.duplicate_async(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.with_raw_response.duplicate_async(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_restore(self, async_client: AsyncMorta) -> None:
        section = await async_client.document.section.restore(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SectionRestoreResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_restore(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.section.with_raw_response.restore(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        section = await response.parse()
        assert_matches_type(SectionRestoreResponse, section, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_restore(self, async_client: AsyncMorta) -> None:
        async with async_client.document.section.with_streaming_response.restore(
            document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            section = await response.parse()
            assert_matches_type(SectionRestoreResponse, section, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_restore(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.section.with_raw_response.restore(
                document_section_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                document_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_section_id` but received ''"):
            await async_client.document.section.with_raw_response.restore(
                document_section_id="",
                document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
