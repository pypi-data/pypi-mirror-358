# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.document import DuplicateGlobalResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDuplicate:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate(self, client: Morta) -> None:
        duplicate = client.document.duplicate.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert duplicate is None

    @pytest.mark.skip()
    @parametrize
    def test_method_duplicate_with_all_params(self, client: Morta) -> None:
        duplicate = client.document.duplicate.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            duplicate_linked_tables=True,
            duplicate_permissions=True,
        )
        assert duplicate is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_duplicate(self, client: Morta) -> None:
        response = client.document.duplicate.with_raw_response.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        duplicate = response.parse()
        assert duplicate is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_duplicate(self, client: Morta) -> None:
        with client.document.duplicate.with_streaming_response.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            duplicate = response.parse()
            assert duplicate is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_duplicate(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.document.duplicate.with_raw_response.duplicate(
                document_id="",
                target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_global(self, client: Morta) -> None:
        duplicate = client.document.duplicate.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_global_with_all_params(self, client: Morta) -> None:
        duplicate = client.document.duplicate.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_global(self, client: Morta) -> None:
        response = client.document.duplicate.with_raw_response.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        duplicate = response.parse()
        assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_global(self, client: Morta) -> None:
        with client.document.duplicate.with_streaming_response.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            duplicate = response.parse()
            assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDuplicate:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate(self, async_client: AsyncMorta) -> None:
        duplicate = await async_client.document.duplicate.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert duplicate is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_duplicate_with_all_params(self, async_client: AsyncMorta) -> None:
        duplicate = await async_client.document.duplicate.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            duplicate_linked_tables=True,
            duplicate_permissions=True,
        )
        assert duplicate is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_duplicate(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.duplicate.with_raw_response.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        duplicate = await response.parse()
        assert duplicate is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_duplicate(self, async_client: AsyncMorta) -> None:
        async with async_client.document.duplicate.with_streaming_response.duplicate(
            document_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            duplicate = await response.parse()
            assert duplicate is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_duplicate(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.document.duplicate.with_raw_response.duplicate(
                document_id="",
                target_project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_global(self, async_client: AsyncMorta) -> None:
        duplicate = await async_client.document.duplicate.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_global_with_all_params(self, async_client: AsyncMorta) -> None:
        duplicate = await async_client.document.duplicate.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_global(self, async_client: AsyncMorta) -> None:
        response = await async_client.document.duplicate.with_raw_response.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        duplicate = await response.parse()
        assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_global(self, async_client: AsyncMorta) -> None:
        async with async_client.document.duplicate.with_streaming_response.global_(
            process_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            duplicate = await response.parse()
            assert_matches_type(DuplicateGlobalResponse, duplicate, path=["response"])

        assert cast(Any, response.is_closed) is True
