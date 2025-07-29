# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

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
from ...types.hub import invite_create_params, invite_update_params
from ..._base_client import make_request_options
from ...types.hub.invite_create_response import InviteCreateResponse
from ...types.hub.invite_delete_response import InviteDeleteResponse
from ...types.hub.invite_resend_response import InviteResendResponse
from ...types.hub.invite_update_response import InviteUpdateResponse

__all__ = ["InviteResource", "AsyncInviteResource"]


class InviteResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InviteResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return InviteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InviteResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return InviteResourceWithStreamingResponse(self)

    def create(
        self,
        hub_id: str,
        *,
        email: str,
        project_role: Literal["member", "admin", "owner"] | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteCreateResponse:
        """Invite a single user to join a hub by email.

        If the user already exists, they
        are added directly; otherwise, an invite is sent. Requires owner or admin
        permissions.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._post(
            f"/v1/hub/{hub_id}/invite",
            body=maybe_transform(
                {
                    "email": email,
                    "project_role": project_role,
                    "tags": tags,
                },
                invite_create_params.InviteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteCreateResponse,
        )

    def update(
        self,
        invite_id: str,
        *,
        hub_id: str,
        project_role: Literal["member", "admin", "owner"] | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteUpdateResponse:
        """
        Update an existing invite in a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return self._put(
            f"/v1/hub/{hub_id}/invite/{invite_id}",
            body=maybe_transform(
                {
                    "project_role": project_role,
                    "tags": tags,
                },
                invite_update_params.InviteUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteUpdateResponse,
        )

    def delete(
        self,
        invite_id: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteDeleteResponse:
        """
        Delete an invite to a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return self._delete(
            f"/v1/hub/{hub_id}/invite/{invite_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteDeleteResponse,
        )

    def resend(
        self,
        invite_id: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteResendResponse:
        """Resend an invitation to a user for a hub.

        This is applicable for both new users
        and existing users who have previously been invited. Requires owner or admin
        permissions.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return self._post(
            f"/v1/hub/{hub_id}/invite/{invite_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteResendResponse,
        )


class AsyncInviteResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInviteResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInviteResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInviteResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncInviteResourceWithStreamingResponse(self)

    async def create(
        self,
        hub_id: str,
        *,
        email: str,
        project_role: Literal["member", "admin", "owner"] | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteCreateResponse:
        """Invite a single user to join a hub by email.

        If the user already exists, they
        are added directly; otherwise, an invite is sent. Requires owner or admin
        permissions.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._post(
            f"/v1/hub/{hub_id}/invite",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "project_role": project_role,
                    "tags": tags,
                },
                invite_create_params.InviteCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteCreateResponse,
        )

    async def update(
        self,
        invite_id: str,
        *,
        hub_id: str,
        project_role: Literal["member", "admin", "owner"] | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteUpdateResponse:
        """
        Update an existing invite in a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return await self._put(
            f"/v1/hub/{hub_id}/invite/{invite_id}",
            body=await async_maybe_transform(
                {
                    "project_role": project_role,
                    "tags": tags,
                },
                invite_update_params.InviteUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteUpdateResponse,
        )

    async def delete(
        self,
        invite_id: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteDeleteResponse:
        """
        Delete an invite to a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return await self._delete(
            f"/v1/hub/{hub_id}/invite/{invite_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteDeleteResponse,
        )

    async def resend(
        self,
        invite_id: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InviteResendResponse:
        """Resend an invitation to a user for a hub.

        This is applicable for both new users
        and existing users who have previously been invited. Requires owner or admin
        permissions.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not invite_id:
            raise ValueError(f"Expected a non-empty value for `invite_id` but received {invite_id!r}")
        return await self._post(
            f"/v1/hub/{hub_id}/invite/{invite_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InviteResendResponse,
        )


class InviteResourceWithRawResponse:
    def __init__(self, invite: InviteResource) -> None:
        self._invite = invite

        self.create = to_raw_response_wrapper(
            invite.create,
        )
        self.update = to_raw_response_wrapper(
            invite.update,
        )
        self.delete = to_raw_response_wrapper(
            invite.delete,
        )
        self.resend = to_raw_response_wrapper(
            invite.resend,
        )


class AsyncInviteResourceWithRawResponse:
    def __init__(self, invite: AsyncInviteResource) -> None:
        self._invite = invite

        self.create = async_to_raw_response_wrapper(
            invite.create,
        )
        self.update = async_to_raw_response_wrapper(
            invite.update,
        )
        self.delete = async_to_raw_response_wrapper(
            invite.delete,
        )
        self.resend = async_to_raw_response_wrapper(
            invite.resend,
        )


class InviteResourceWithStreamingResponse:
    def __init__(self, invite: InviteResource) -> None:
        self._invite = invite

        self.create = to_streamed_response_wrapper(
            invite.create,
        )
        self.update = to_streamed_response_wrapper(
            invite.update,
        )
        self.delete = to_streamed_response_wrapper(
            invite.delete,
        )
        self.resend = to_streamed_response_wrapper(
            invite.resend,
        )


class AsyncInviteResourceWithStreamingResponse:
    def __init__(self, invite: AsyncInviteResource) -> None:
        self._invite = invite

        self.create = async_to_streamed_response_wrapper(
            invite.create,
        )
        self.update = async_to_streamed_response_wrapper(
            invite.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            invite.delete,
        )
        self.resend = async_to_streamed_response_wrapper(
            invite.resend,
        )
