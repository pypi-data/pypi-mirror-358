# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.hub import ai_answer_vote_params
from ..._base_client import make_request_options
from ...types.hub.ai_answer_vote_response import AIAnswerVoteResponse

__all__ = ["AIAnswerResource", "AsyncAIAnswerResource"]


class AIAnswerResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AIAnswerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AIAnswerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AIAnswerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AIAnswerResourceWithStreamingResponse(self)

    def vote(
        self,
        answer_id: str,
        *,
        hub_id: str,
        comment: str | NotGiven = NOT_GIVEN,
        vote: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIAnswerVoteResponse:
        """
        Vote on an AI answer within a specific hub, identified by the hub's UUID and the
        answer's UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not answer_id:
            raise ValueError(f"Expected a non-empty value for `answer_id` but received {answer_id!r}")
        return self._post(
            f"/v1/hub/{hub_id}/ai-answer/{answer_id}/vote",
            body=maybe_transform(
                {
                    "comment": comment,
                    "vote": vote,
                },
                ai_answer_vote_params.AIAnswerVoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIAnswerVoteResponse,
        )


class AsyncAIAnswerResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAIAnswerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAIAnswerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAIAnswerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncAIAnswerResourceWithStreamingResponse(self)

    async def vote(
        self,
        answer_id: str,
        *,
        hub_id: str,
        comment: str | NotGiven = NOT_GIVEN,
        vote: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AIAnswerVoteResponse:
        """
        Vote on an AI answer within a specific hub, identified by the hub's UUID and the
        answer's UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not answer_id:
            raise ValueError(f"Expected a non-empty value for `answer_id` but received {answer_id!r}")
        return await self._post(
            f"/v1/hub/{hub_id}/ai-answer/{answer_id}/vote",
            body=await async_maybe_transform(
                {
                    "comment": comment,
                    "vote": vote,
                },
                ai_answer_vote_params.AIAnswerVoteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AIAnswerVoteResponse,
        )


class AIAnswerResourceWithRawResponse:
    def __init__(self, ai_answer: AIAnswerResource) -> None:
        self._ai_answer = ai_answer

        self.vote = to_raw_response_wrapper(
            ai_answer.vote,
        )


class AsyncAIAnswerResourceWithRawResponse:
    def __init__(self, ai_answer: AsyncAIAnswerResource) -> None:
        self._ai_answer = ai_answer

        self.vote = async_to_raw_response_wrapper(
            ai_answer.vote,
        )


class AIAnswerResourceWithStreamingResponse:
    def __init__(self, ai_answer: AIAnswerResource) -> None:
        self._ai_answer = ai_answer

        self.vote = to_streamed_response_wrapper(
            ai_answer.vote,
        )


class AsyncAIAnswerResourceWithStreamingResponse:
    def __init__(self, ai_answer: AsyncAIAnswerResource) -> None:
        self._ai_answer = ai_answer

        self.vote = async_to_streamed_response_wrapper(
            ai_answer.vote,
        )
