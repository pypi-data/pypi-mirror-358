# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from morta.types import (
    CommentThreadListResponse,
    CommentThreadCreateResponse,
    CommentThreadDeleteResponse,
    CommentThreadReopenResponse,
    CommentThreadResolveResponse,
    CommentThreadGetStatsResponse,
    CommentThreadRetrieveResponse,
)
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCommentThread:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Morta) -> None:
        comment_thread = client.comment_thread.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
        )
        assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Morta) -> None:
        comment_thread = client.comment_thread.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            main_reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Morta) -> None:
        comment_thread = client.comment_thread.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadRetrieveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadRetrieveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadRetrieveResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Morta) -> None:
        comment_thread = client.comment_thread.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
        )
        assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Morta) -> None:
        comment_thread = client.comment_thread.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
            main_reference="main_reference",
        )
        assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Morta) -> None:
        comment_thread = client.comment_thread.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadDeleteResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadDeleteResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadDeleteResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_stats(self, client: Morta) -> None:
        comment_thread = client.comment_thread.get_stats(
            reference_type="process_section",
        )
        assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_stats_with_all_params(self, client: Morta) -> None:
        comment_thread = client.comment_thread.get_stats(
            reference_type="process_section",
            main_reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_stats(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.get_stats(
            reference_type="process_section",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_stats(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.get_stats(
            reference_type="process_section",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_reopen(self, client: Morta) -> None:
        comment_thread = client.comment_thread.reopen(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadReopenResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_reopen(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.reopen(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadReopenResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_reopen(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.reopen(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadReopenResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_reopen(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.with_raw_response.reopen(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_resolve(self, client: Morta) -> None:
        comment_thread = client.comment_thread.resolve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadResolveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_resolve(self, client: Morta) -> None:
        response = client.comment_thread.with_raw_response.resolve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = response.parse()
        assert_matches_type(CommentThreadResolveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_resolve(self, client: Morta) -> None:
        with client.comment_thread.with_streaming_response.resolve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = response.parse()
            assert_matches_type(CommentThreadResolveResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_resolve(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            client.comment_thread.with_raw_response.resolve(
                "",
            )


class TestAsyncCommentThread:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
        )
        assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
            context={
                "process_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_response_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "process_section_public_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                "project_id": "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            },
            main_reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.create(
            comment_text="commentText",
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="referenceType",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadCreateResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadRetrieveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadRetrieveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadRetrieveResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
        )
        assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
            main_reference="main_reference",
        )
        assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.list(
            reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            reference_type="process_section",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadListResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadDeleteResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadDeleteResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.delete(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadDeleteResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_stats(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.get_stats(
            reference_type="process_section",
        )
        assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_stats_with_all_params(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.get_stats(
            reference_type="process_section",
            main_reference_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_stats(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.get_stats(
            reference_type="process_section",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_stats(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.get_stats(
            reference_type="process_section",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadGetStatsResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_reopen(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.reopen(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadReopenResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_reopen(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.reopen(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadReopenResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_reopen(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.reopen(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadReopenResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_reopen(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.with_raw_response.reopen(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_resolve(self, async_client: AsyncMorta) -> None:
        comment_thread = await async_client.comment_thread.resolve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(CommentThreadResolveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_resolve(self, async_client: AsyncMorta) -> None:
        response = await async_client.comment_thread.with_raw_response.resolve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        comment_thread = await response.parse()
        assert_matches_type(CommentThreadResolveResponse, comment_thread, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_resolve(self, async_client: AsyncMorta) -> None:
        async with async_client.comment_thread.with_streaming_response.resolve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            comment_thread = await response.parse()
            assert_matches_type(CommentThreadResolveResponse, comment_thread, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_resolve(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `comment_thread_id` but received ''"):
            await async_client.comment_thread.with_raw_response.resolve(
                "",
            )
