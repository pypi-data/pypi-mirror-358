# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.user.hub_list_response import HubListResponse
from ...types.user.hub_list_tags_response import HubListTagsResponse
from ...types.user.hub_toggle_pin_response import HubTogglePinResponse
from ...types.user.hub_list_favourites_response import HubListFavouritesResponse
from ...types.user.hub_toggle_favourite_response import HubToggleFavouriteResponse

__all__ = ["HubsResource", "AsyncHubsResource"]


class HubsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HubsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return HubsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HubsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return HubsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubListResponse:
        """Get all hubs the currently logged in user is part of"""
        return self._get(
            "/v1/user/hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubListResponse,
        )

    def list_favourites(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubListFavouritesResponse:
        """Get all favourite hubs the currently logged in user is part of"""
        return self._get(
            "/v1/user/hubs/favourites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubListFavouritesResponse,
        )

    def list_tags(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubListTagsResponse:
        """
        Get all tags for current user in a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._put(
            f"/v1/user/hubs/{hub_id}/tags",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubListTagsResponse,
        )

    def toggle_favourite(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubToggleFavouriteResponse:
        """
        Change whether the hub is a favourite for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._put(
            f"/v1/user/hubs/{hub_id}/favourite",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubToggleFavouriteResponse,
        )

    def toggle_pin(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubTogglePinResponse:
        """
        Change whether the hub is pinned for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._put(
            f"/v1/user/hubs/{hub_id}/pin",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubTogglePinResponse,
        )


class AsyncHubsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHubsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncHubsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHubsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncHubsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubListResponse:
        """Get all hubs the currently logged in user is part of"""
        return await self._get(
            "/v1/user/hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubListResponse,
        )

    async def list_favourites(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubListFavouritesResponse:
        """Get all favourite hubs the currently logged in user is part of"""
        return await self._get(
            "/v1/user/hubs/favourites",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubListFavouritesResponse,
        )

    async def list_tags(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubListTagsResponse:
        """
        Get all tags for current user in a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._put(
            f"/v1/user/hubs/{hub_id}/tags",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubListTagsResponse,
        )

    async def toggle_favourite(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubToggleFavouriteResponse:
        """
        Change whether the hub is a favourite for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._put(
            f"/v1/user/hubs/{hub_id}/favourite",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubToggleFavouriteResponse,
        )

    async def toggle_pin(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubTogglePinResponse:
        """
        Change whether the hub is pinned for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._put(
            f"/v1/user/hubs/{hub_id}/pin",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubTogglePinResponse,
        )


class HubsResourceWithRawResponse:
    def __init__(self, hubs: HubsResource) -> None:
        self._hubs = hubs

        self.list = to_raw_response_wrapper(
            hubs.list,
        )
        self.list_favourites = to_raw_response_wrapper(
            hubs.list_favourites,
        )
        self.list_tags = to_raw_response_wrapper(
            hubs.list_tags,
        )
        self.toggle_favourite = to_raw_response_wrapper(
            hubs.toggle_favourite,
        )
        self.toggle_pin = to_raw_response_wrapper(
            hubs.toggle_pin,
        )


class AsyncHubsResourceWithRawResponse:
    def __init__(self, hubs: AsyncHubsResource) -> None:
        self._hubs = hubs

        self.list = async_to_raw_response_wrapper(
            hubs.list,
        )
        self.list_favourites = async_to_raw_response_wrapper(
            hubs.list_favourites,
        )
        self.list_tags = async_to_raw_response_wrapper(
            hubs.list_tags,
        )
        self.toggle_favourite = async_to_raw_response_wrapper(
            hubs.toggle_favourite,
        )
        self.toggle_pin = async_to_raw_response_wrapper(
            hubs.toggle_pin,
        )


class HubsResourceWithStreamingResponse:
    def __init__(self, hubs: HubsResource) -> None:
        self._hubs = hubs

        self.list = to_streamed_response_wrapper(
            hubs.list,
        )
        self.list_favourites = to_streamed_response_wrapper(
            hubs.list_favourites,
        )
        self.list_tags = to_streamed_response_wrapper(
            hubs.list_tags,
        )
        self.toggle_favourite = to_streamed_response_wrapper(
            hubs.toggle_favourite,
        )
        self.toggle_pin = to_streamed_response_wrapper(
            hubs.toggle_pin,
        )


class AsyncHubsResourceWithStreamingResponse:
    def __init__(self, hubs: AsyncHubsResource) -> None:
        self._hubs = hubs

        self.list = async_to_streamed_response_wrapper(
            hubs.list,
        )
        self.list_favourites = async_to_streamed_response_wrapper(
            hubs.list_favourites,
        )
        self.list_tags = async_to_streamed_response_wrapper(
            hubs.list_tags,
        )
        self.toggle_favourite = async_to_streamed_response_wrapper(
            hubs.toggle_favourite,
        )
        self.toggle_pin = async_to_streamed_response_wrapper(
            hubs.toggle_pin,
        )
