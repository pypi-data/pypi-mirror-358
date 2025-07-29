# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from morta import Morta, AsyncMorta
from tests.utils import assert_matches_type
from morta.types.hub import AIAnswerVoteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAIAnswer:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_vote(self, client: Morta) -> None:
        ai_answer = client.hub.ai_answer.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_vote_with_all_params(self, client: Morta) -> None:
        ai_answer = client.hub.ai_answer.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment="comment",
            vote=True,
        )
        assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_vote(self, client: Morta) -> None:
        response = client.hub.ai_answer.with_raw_response.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ai_answer = response.parse()
        assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_vote(self, client: Morta) -> None:
        with client.hub.ai_answer.with_streaming_response.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ai_answer = response.parse()
            assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_vote(self, client: Morta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            client.hub.ai_answer.with_raw_response.vote(
                answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `answer_id` but received ''"):
            client.hub.ai_answer.with_raw_response.vote(
                answer_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )


class TestAsyncAIAnswer:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_vote(self, async_client: AsyncMorta) -> None:
        ai_answer = await async_client.hub.ai_answer.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_vote_with_all_params(self, async_client: AsyncMorta) -> None:
        ai_answer = await async_client.hub.ai_answer.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            comment="comment",
            vote=True,
        )
        assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_vote(self, async_client: AsyncMorta) -> None:
        response = await async_client.hub.ai_answer.with_raw_response.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ai_answer = await response.parse()
        assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_vote(self, async_client: AsyncMorta) -> None:
        async with async_client.hub.ai_answer.with_streaming_response.vote(
            answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ai_answer = await response.parse()
            assert_matches_type(AIAnswerVoteResponse, ai_answer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_vote(self, async_client: AsyncMorta) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `hub_id` but received ''"):
            await async_client.hub.ai_answer.with_raw_response.vote(
                answer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
                hub_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `answer_id` but received ''"):
            await async_client.hub.ai_answer.with_raw_response.vote(
                answer_id="",
                hub_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            )
