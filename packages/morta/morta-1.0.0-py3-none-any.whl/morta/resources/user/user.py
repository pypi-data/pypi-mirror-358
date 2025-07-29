# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from .hubs import (
    HubsResource,
    AsyncHubsResource,
    HubsResourceWithRawResponse,
    AsyncHubsResourceWithRawResponse,
    HubsResourceWithStreamingResponse,
    AsyncHubsResourceWithStreamingResponse,
)
from .tags import (
    TagsResource,
    AsyncTagsResource,
    TagsResourceWithRawResponse,
    AsyncTagsResourceWithRawResponse,
    TagsResourceWithStreamingResponse,
    AsyncTagsResourceWithStreamingResponse,
)
from .apikey import (
    ApikeyResource,
    AsyncApikeyResource,
    ApikeyResourceWithRawResponse,
    AsyncApikeyResourceWithRawResponse,
    ApikeyResourceWithStreamingResponse,
    AsyncApikeyResourceWithStreamingResponse,
)
from ...types import user_create_params, user_search_params, user_update_account_params, user_update_profile_params
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
from ..._base_client import make_request_options
from ...types.user_create_response import UserCreateResponse
from ...types.user_search_response import UserSearchResponse
from ...types.user_retrieve_response import UserRetrieveResponse
from ...types.user_retrieve_me_response import UserRetrieveMeResponse
from ...types.user_list_templates_response import UserListTemplatesResponse
from ...types.user_update_account_response import UserUpdateAccountResponse
from ...types.user_update_profile_response import UserUpdateProfileResponse
from ...types.user_list_owner_hubs_response import UserListOwnerHubsResponse
from ...types.user_list_pinned_hubs_response import UserListPinnedHubsResponse
from ...types.user_list_public_hubs_response import UserListPublicHubsResponse
from ...types.user_list_achievements_response import UserListAchievementsResponse
from ...types.user_list_contributions_response import UserListContributionsResponse
from ...types.user_retrieve_by_public_id_response import UserRetrieveByPublicIDResponse
from ...types.user_list_public_contributions_response import UserListPublicContributionsResponse

__all__ = ["UserResource", "AsyncUserResource"]


class UserResource(SyncAPIResource):
    @cached_property
    def apikey(self) -> ApikeyResource:
        return ApikeyResource(self._client)

    @cached_property
    def hubs(self) -> HubsResource:
        return HubsResource(self._client)

    @cached_property
    def tags(self) -> TagsResource:
        return TagsResource(self._client)

    @cached_property
    def with_raw_response(self) -> UserResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return UserResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return UserResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        email: str,
        name: str,
        password: str,
        opt_out_ai_email: bool | NotGiven = NOT_GIVEN,
        opt_out_duplication_email: bool | NotGiven = NOT_GIVEN,
        opt_out_hub_email: bool | NotGiven = NOT_GIVEN,
        opt_out_sync_email: bool | NotGiven = NOT_GIVEN,
        opt_out_welcome_email: bool | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        template: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserCreateResponse:
        """
        Create a new user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/user",
            body=maybe_transform(
                {
                    "email": email,
                    "name": name,
                    "password": password,
                    "opt_out_ai_email": opt_out_ai_email,
                    "opt_out_duplication_email": opt_out_duplication_email,
                    "opt_out_hub_email": opt_out_hub_email,
                    "opt_out_sync_email": opt_out_sync_email,
                    "opt_out_welcome_email": opt_out_welcome_email,
                    "project_id": project_id,
                    "template": template,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserCreateResponse,
        )

    def retrieve(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserRetrieveResponse:
        """
        Get information on a specific user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._get(
            f"/v1/user/{firebase_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserRetrieveResponse,
        )

    def list_achievements(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListAchievementsResponse:
        """
        Get the achievement badges of a user by their Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._get(
            f"/v1/user/{firebase_id}/achievements",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListAchievementsResponse,
        )

    def list_contributions(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListContributionsResponse:
        """
        Get the number of contributions per day made by a user, identified by their
        Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._get(
            f"/v1/user/{firebase_id}/contributions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListContributionsResponse,
        )

    def list_owner_hubs(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListOwnerHubsResponse:
        """Get all hubs where the user is the owner or an admin"""
        return self._get(
            "/v1/user/owner-hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListOwnerHubsResponse,
        )

    def list_pinned_hubs(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListPinnedHubsResponse:
        """
        Get the hubs pinned by a user identified by their Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._get(
            f"/v1/user/{firebase_id}/pinned-hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListPinnedHubsResponse,
        )

    def list_public_contributions(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListPublicContributionsResponse:
        """
        Get the public contributions made by a user, identified by their Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._get(
            f"/v1/user/{firebase_id}/public-contributions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListPublicContributionsResponse,
        )

    def list_public_hubs(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListPublicHubsResponse:
        """Get all public hubs where the user is a member"""
        return self._get(
            "/v1/user/public-hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListPublicHubsResponse,
        )

    def list_templates(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListTemplatesResponse:
        """Get all templates the currently logged in user has access to"""
        return self._get(
            "/v1/user/templates",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListTemplatesResponse,
        )

    def retrieve_by_public_id(
        self,
        public_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserRetrieveByPublicIDResponse:
        """
        Get information on a specific user by their public ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not public_id:
            raise ValueError(f"Expected a non-empty value for `public_id` but received {public_id!r}")
        return self._get(
            f"/v1/user/public/{public_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserRetrieveByPublicIDResponse,
        )

    def retrieve_me(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserRetrieveMeResponse:
        """Get info on the current user"""
        return self._get(
            "/v1/user/me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserRetrieveMeResponse,
        )

    def search(
        self,
        *,
        query: str,
        process_id: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        table_view_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserSearchResponse:
        """
        Search for users by hub or process

        Args:
          query: Query string for searching users

          process_id: Process ID to restrict search

          project_id: Hub ID to restrict search

          table_view_id: Table View ID to restrict search

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/user/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "query": query,
                        "process_id": process_id,
                        "project_id": project_id,
                        "table_view_id": table_view_id,
                    },
                    user_search_params.UserSearchParams,
                ),
            ),
            cast_to=UserSearchResponse,
        )

    def update_account(
        self,
        *,
        allow_support_access: Optional[bool] | NotGiven = NOT_GIVEN,
        old_password: str | NotGiven = NOT_GIVEN,
        opt_out_ai_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_duplication_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_hub_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_sync_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_welcome_email: Optional[bool] | NotGiven = NOT_GIVEN,
        password: str | NotGiven = NOT_GIVEN,
        password_confirm: str | NotGiven = NOT_GIVEN,
        two_factor_code: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserUpdateAccountResponse:
        """
        Update the account details for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/v1/user/account",
            body=maybe_transform(
                {
                    "allow_support_access": allow_support_access,
                    "old_password": old_password,
                    "opt_out_ai_email": opt_out_ai_email,
                    "opt_out_duplication_email": opt_out_duplication_email,
                    "opt_out_hub_email": opt_out_hub_email,
                    "opt_out_sync_email": opt_out_sync_email,
                    "opt_out_welcome_email": opt_out_welcome_email,
                    "password": password,
                    "password_confirm": password_confirm,
                    "two_factor_code": two_factor_code,
                },
                user_update_account_params.UserUpdateAccountParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserUpdateAccountResponse,
        )

    def update_profile(
        self,
        *,
        allow_support_access: Optional[bool] | NotGiven = NOT_GIVEN,
        bio: Optional[str] | NotGiven = NOT_GIVEN,
        linkedin: Optional[str] | NotGiven = NOT_GIVEN,
        location: Optional[str] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        organisation: Optional[str] | NotGiven = NOT_GIVEN,
        profile_picture: Optional[str] | NotGiven = NOT_GIVEN,
        twitter: Optional[str] | NotGiven = NOT_GIVEN,
        university: Optional[str] | NotGiven = NOT_GIVEN,
        university_degree: Optional[str] | NotGiven = NOT_GIVEN,
        website: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserUpdateProfileResponse:
        """
        Update the profile of the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/v1/user",
            body=maybe_transform(
                {
                    "allow_support_access": allow_support_access,
                    "bio": bio,
                    "linkedin": linkedin,
                    "location": location,
                    "name": name,
                    "organisation": organisation,
                    "profile_picture": profile_picture,
                    "twitter": twitter,
                    "university": university,
                    "university_degree": university_degree,
                    "website": website,
                },
                user_update_profile_params.UserUpdateProfileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserUpdateProfileResponse,
        )


class AsyncUserResource(AsyncAPIResource):
    @cached_property
    def apikey(self) -> AsyncApikeyResource:
        return AsyncApikeyResource(self._client)

    @cached_property
    def hubs(self) -> AsyncHubsResource:
        return AsyncHubsResource(self._client)

    @cached_property
    def tags(self) -> AsyncTagsResource:
        return AsyncTagsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncUserResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUserResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncUserResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        email: str,
        name: str,
        password: str,
        opt_out_ai_email: bool | NotGiven = NOT_GIVEN,
        opt_out_duplication_email: bool | NotGiven = NOT_GIVEN,
        opt_out_hub_email: bool | NotGiven = NOT_GIVEN,
        opt_out_sync_email: bool | NotGiven = NOT_GIVEN,
        opt_out_welcome_email: bool | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        template: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserCreateResponse:
        """
        Create a new user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/user",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "name": name,
                    "password": password,
                    "opt_out_ai_email": opt_out_ai_email,
                    "opt_out_duplication_email": opt_out_duplication_email,
                    "opt_out_hub_email": opt_out_hub_email,
                    "opt_out_sync_email": opt_out_sync_email,
                    "opt_out_welcome_email": opt_out_welcome_email,
                    "project_id": project_id,
                    "template": template,
                },
                user_create_params.UserCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserCreateResponse,
        )

    async def retrieve(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserRetrieveResponse:
        """
        Get information on a specific user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._get(
            f"/v1/user/{firebase_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserRetrieveResponse,
        )

    async def list_achievements(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListAchievementsResponse:
        """
        Get the achievement badges of a user by their Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._get(
            f"/v1/user/{firebase_id}/achievements",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListAchievementsResponse,
        )

    async def list_contributions(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListContributionsResponse:
        """
        Get the number of contributions per day made by a user, identified by their
        Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._get(
            f"/v1/user/{firebase_id}/contributions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListContributionsResponse,
        )

    async def list_owner_hubs(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListOwnerHubsResponse:
        """Get all hubs where the user is the owner or an admin"""
        return await self._get(
            "/v1/user/owner-hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListOwnerHubsResponse,
        )

    async def list_pinned_hubs(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListPinnedHubsResponse:
        """
        Get the hubs pinned by a user identified by their Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._get(
            f"/v1/user/{firebase_id}/pinned-hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListPinnedHubsResponse,
        )

    async def list_public_contributions(
        self,
        firebase_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListPublicContributionsResponse:
        """
        Get the public contributions made by a user, identified by their Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._get(
            f"/v1/user/{firebase_id}/public-contributions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListPublicContributionsResponse,
        )

    async def list_public_hubs(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListPublicHubsResponse:
        """Get all public hubs where the user is a member"""
        return await self._get(
            "/v1/user/public-hubs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListPublicHubsResponse,
        )

    async def list_templates(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserListTemplatesResponse:
        """Get all templates the currently logged in user has access to"""
        return await self._get(
            "/v1/user/templates",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserListTemplatesResponse,
        )

    async def retrieve_by_public_id(
        self,
        public_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserRetrieveByPublicIDResponse:
        """
        Get information on a specific user by their public ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not public_id:
            raise ValueError(f"Expected a non-empty value for `public_id` but received {public_id!r}")
        return await self._get(
            f"/v1/user/public/{public_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserRetrieveByPublicIDResponse,
        )

    async def retrieve_me(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserRetrieveMeResponse:
        """Get info on the current user"""
        return await self._get(
            "/v1/user/me",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserRetrieveMeResponse,
        )

    async def search(
        self,
        *,
        query: str,
        process_id: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        table_view_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserSearchResponse:
        """
        Search for users by hub or process

        Args:
          query: Query string for searching users

          process_id: Process ID to restrict search

          project_id: Hub ID to restrict search

          table_view_id: Table View ID to restrict search

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/user/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "query": query,
                        "process_id": process_id,
                        "project_id": project_id,
                        "table_view_id": table_view_id,
                    },
                    user_search_params.UserSearchParams,
                ),
            ),
            cast_to=UserSearchResponse,
        )

    async def update_account(
        self,
        *,
        allow_support_access: Optional[bool] | NotGiven = NOT_GIVEN,
        old_password: str | NotGiven = NOT_GIVEN,
        opt_out_ai_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_duplication_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_hub_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_sync_email: Optional[bool] | NotGiven = NOT_GIVEN,
        opt_out_welcome_email: Optional[bool] | NotGiven = NOT_GIVEN,
        password: str | NotGiven = NOT_GIVEN,
        password_confirm: str | NotGiven = NOT_GIVEN,
        two_factor_code: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserUpdateAccountResponse:
        """
        Update the account details for the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/v1/user/account",
            body=await async_maybe_transform(
                {
                    "allow_support_access": allow_support_access,
                    "old_password": old_password,
                    "opt_out_ai_email": opt_out_ai_email,
                    "opt_out_duplication_email": opt_out_duplication_email,
                    "opt_out_hub_email": opt_out_hub_email,
                    "opt_out_sync_email": opt_out_sync_email,
                    "opt_out_welcome_email": opt_out_welcome_email,
                    "password": password,
                    "password_confirm": password_confirm,
                    "two_factor_code": two_factor_code,
                },
                user_update_account_params.UserUpdateAccountParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserUpdateAccountResponse,
        )

    async def update_profile(
        self,
        *,
        allow_support_access: Optional[bool] | NotGiven = NOT_GIVEN,
        bio: Optional[str] | NotGiven = NOT_GIVEN,
        linkedin: Optional[str] | NotGiven = NOT_GIVEN,
        location: Optional[str] | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        organisation: Optional[str] | NotGiven = NOT_GIVEN,
        profile_picture: Optional[str] | NotGiven = NOT_GIVEN,
        twitter: Optional[str] | NotGiven = NOT_GIVEN,
        university: Optional[str] | NotGiven = NOT_GIVEN,
        university_degree: Optional[str] | NotGiven = NOT_GIVEN,
        website: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserUpdateProfileResponse:
        """
        Update the profile of the currently logged in user

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/v1/user",
            body=await async_maybe_transform(
                {
                    "allow_support_access": allow_support_access,
                    "bio": bio,
                    "linkedin": linkedin,
                    "location": location,
                    "name": name,
                    "organisation": organisation,
                    "profile_picture": profile_picture,
                    "twitter": twitter,
                    "university": university,
                    "university_degree": university_degree,
                    "website": website,
                },
                user_update_profile_params.UserUpdateProfileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserUpdateProfileResponse,
        )


class UserResourceWithRawResponse:
    def __init__(self, user: UserResource) -> None:
        self._user = user

        self.create = to_raw_response_wrapper(
            user.create,
        )
        self.retrieve = to_raw_response_wrapper(
            user.retrieve,
        )
        self.list_achievements = to_raw_response_wrapper(
            user.list_achievements,
        )
        self.list_contributions = to_raw_response_wrapper(
            user.list_contributions,
        )
        self.list_owner_hubs = to_raw_response_wrapper(
            user.list_owner_hubs,
        )
        self.list_pinned_hubs = to_raw_response_wrapper(
            user.list_pinned_hubs,
        )
        self.list_public_contributions = to_raw_response_wrapper(
            user.list_public_contributions,
        )
        self.list_public_hubs = to_raw_response_wrapper(
            user.list_public_hubs,
        )
        self.list_templates = to_raw_response_wrapper(
            user.list_templates,
        )
        self.retrieve_by_public_id = to_raw_response_wrapper(
            user.retrieve_by_public_id,
        )
        self.retrieve_me = to_raw_response_wrapper(
            user.retrieve_me,
        )
        self.search = to_raw_response_wrapper(
            user.search,
        )
        self.update_account = to_raw_response_wrapper(
            user.update_account,
        )
        self.update_profile = to_raw_response_wrapper(
            user.update_profile,
        )

    @cached_property
    def apikey(self) -> ApikeyResourceWithRawResponse:
        return ApikeyResourceWithRawResponse(self._user.apikey)

    @cached_property
    def hubs(self) -> HubsResourceWithRawResponse:
        return HubsResourceWithRawResponse(self._user.hubs)

    @cached_property
    def tags(self) -> TagsResourceWithRawResponse:
        return TagsResourceWithRawResponse(self._user.tags)


class AsyncUserResourceWithRawResponse:
    def __init__(self, user: AsyncUserResource) -> None:
        self._user = user

        self.create = async_to_raw_response_wrapper(
            user.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            user.retrieve,
        )
        self.list_achievements = async_to_raw_response_wrapper(
            user.list_achievements,
        )
        self.list_contributions = async_to_raw_response_wrapper(
            user.list_contributions,
        )
        self.list_owner_hubs = async_to_raw_response_wrapper(
            user.list_owner_hubs,
        )
        self.list_pinned_hubs = async_to_raw_response_wrapper(
            user.list_pinned_hubs,
        )
        self.list_public_contributions = async_to_raw_response_wrapper(
            user.list_public_contributions,
        )
        self.list_public_hubs = async_to_raw_response_wrapper(
            user.list_public_hubs,
        )
        self.list_templates = async_to_raw_response_wrapper(
            user.list_templates,
        )
        self.retrieve_by_public_id = async_to_raw_response_wrapper(
            user.retrieve_by_public_id,
        )
        self.retrieve_me = async_to_raw_response_wrapper(
            user.retrieve_me,
        )
        self.search = async_to_raw_response_wrapper(
            user.search,
        )
        self.update_account = async_to_raw_response_wrapper(
            user.update_account,
        )
        self.update_profile = async_to_raw_response_wrapper(
            user.update_profile,
        )

    @cached_property
    def apikey(self) -> AsyncApikeyResourceWithRawResponse:
        return AsyncApikeyResourceWithRawResponse(self._user.apikey)

    @cached_property
    def hubs(self) -> AsyncHubsResourceWithRawResponse:
        return AsyncHubsResourceWithRawResponse(self._user.hubs)

    @cached_property
    def tags(self) -> AsyncTagsResourceWithRawResponse:
        return AsyncTagsResourceWithRawResponse(self._user.tags)


class UserResourceWithStreamingResponse:
    def __init__(self, user: UserResource) -> None:
        self._user = user

        self.create = to_streamed_response_wrapper(
            user.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            user.retrieve,
        )
        self.list_achievements = to_streamed_response_wrapper(
            user.list_achievements,
        )
        self.list_contributions = to_streamed_response_wrapper(
            user.list_contributions,
        )
        self.list_owner_hubs = to_streamed_response_wrapper(
            user.list_owner_hubs,
        )
        self.list_pinned_hubs = to_streamed_response_wrapper(
            user.list_pinned_hubs,
        )
        self.list_public_contributions = to_streamed_response_wrapper(
            user.list_public_contributions,
        )
        self.list_public_hubs = to_streamed_response_wrapper(
            user.list_public_hubs,
        )
        self.list_templates = to_streamed_response_wrapper(
            user.list_templates,
        )
        self.retrieve_by_public_id = to_streamed_response_wrapper(
            user.retrieve_by_public_id,
        )
        self.retrieve_me = to_streamed_response_wrapper(
            user.retrieve_me,
        )
        self.search = to_streamed_response_wrapper(
            user.search,
        )
        self.update_account = to_streamed_response_wrapper(
            user.update_account,
        )
        self.update_profile = to_streamed_response_wrapper(
            user.update_profile,
        )

    @cached_property
    def apikey(self) -> ApikeyResourceWithStreamingResponse:
        return ApikeyResourceWithStreamingResponse(self._user.apikey)

    @cached_property
    def hubs(self) -> HubsResourceWithStreamingResponse:
        return HubsResourceWithStreamingResponse(self._user.hubs)

    @cached_property
    def tags(self) -> TagsResourceWithStreamingResponse:
        return TagsResourceWithStreamingResponse(self._user.tags)


class AsyncUserResourceWithStreamingResponse:
    def __init__(self, user: AsyncUserResource) -> None:
        self._user = user

        self.create = async_to_streamed_response_wrapper(
            user.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            user.retrieve,
        )
        self.list_achievements = async_to_streamed_response_wrapper(
            user.list_achievements,
        )
        self.list_contributions = async_to_streamed_response_wrapper(
            user.list_contributions,
        )
        self.list_owner_hubs = async_to_streamed_response_wrapper(
            user.list_owner_hubs,
        )
        self.list_pinned_hubs = async_to_streamed_response_wrapper(
            user.list_pinned_hubs,
        )
        self.list_public_contributions = async_to_streamed_response_wrapper(
            user.list_public_contributions,
        )
        self.list_public_hubs = async_to_streamed_response_wrapper(
            user.list_public_hubs,
        )
        self.list_templates = async_to_streamed_response_wrapper(
            user.list_templates,
        )
        self.retrieve_by_public_id = async_to_streamed_response_wrapper(
            user.retrieve_by_public_id,
        )
        self.retrieve_me = async_to_streamed_response_wrapper(
            user.retrieve_me,
        )
        self.search = async_to_streamed_response_wrapper(
            user.search,
        )
        self.update_account = async_to_streamed_response_wrapper(
            user.update_account,
        )
        self.update_profile = async_to_streamed_response_wrapper(
            user.update_profile,
        )

    @cached_property
    def apikey(self) -> AsyncApikeyResourceWithStreamingResponse:
        return AsyncApikeyResourceWithStreamingResponse(self._user.apikey)

    @cached_property
    def hubs(self) -> AsyncHubsResourceWithStreamingResponse:
        return AsyncHubsResourceWithStreamingResponse(self._user.hubs)

    @cached_property
    def tags(self) -> AsyncTagsResourceWithStreamingResponse:
        return AsyncTagsResourceWithStreamingResponse(self._user.tags)
