# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import (
    permission_create_params,
    permission_update_params,
    permission_retrieve_params,
    permission_create_all_params,
    permission_retrieve_tag_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.base_request_context_param import BaseRequestContextParam
from ..types.permission_create_response import PermissionCreateResponse
from ..types.permission_update_response import PermissionUpdateResponse
from ..types.permission_retrieve_response import PermissionRetrieveResponse
from ..types.permission_create_all_response import PermissionCreateAllResponse
from ..types.permission_retrieve_tag_response import PermissionRetrieveTagResponse

__all__ = ["PermissionsResource", "AsyncPermissionsResource"]


class PermissionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PermissionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return PermissionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PermissionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return PermissionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        attribute_kind: Literal["user", "tag", "project", "all_table_tags"],
        resource_id: str,
        resource_kind: Literal["process", "table", "table_view"],
        role: Literal[0, 1, 2, 3, 4],
        attribute_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        tag_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionCreateResponse:
        """
        Create permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/permissions",
            body=maybe_transform(
                {
                    "attribute_kind": attribute_kind,
                    "resource_id": resource_id,
                    "resource_kind": resource_kind,
                    "role": role,
                    "attribute_id": attribute_id,
                    "context": context,
                    "tag_reference_id": tag_reference_id,
                },
                permission_create_params.PermissionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionCreateResponse,
        )

    def retrieve(
        self,
        *,
        resource: Literal["process", "table", "table_view"],
        resource_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionRetrieveResponse:
        """
        Retrieve permissions for a specified resource, such as a table, table view, or
        process.

        Args:
          resource: The kind of resource for which to retrieve permissions. Valid options are
              'process', 'table', or 'table_view'.

          resource_id: UUID of the resource for which to retrieve permissions.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/permissions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "resource": resource,
                        "resource_id": resource_id,
                    },
                    permission_retrieve_params.PermissionRetrieveParams,
                ),
            ),
            cast_to=PermissionRetrieveResponse,
        )

    def update(
        self,
        id: str,
        *,
        role: Literal[0, 1, 2, 3, 4],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionUpdateResponse:
        """
        Update permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/v1/permissions/{id}",
            body=maybe_transform(
                {
                    "role": role,
                    "context": context,
                },
                permission_update_params.PermissionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionUpdateResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/permissions/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def create_all(
        self,
        *,
        attribute_kind: Literal["user", "tag", "project", "all_table_tags"],
        resource_id: str,
        resource_kind: Literal["process", "table", "table_view"],
        role: Literal[0, 1, 2, 3, 4],
        attribute_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        tag_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionCreateAllResponse:
        """
        Create permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/permissions/all",
            body=maybe_transform(
                {
                    "attribute_kind": attribute_kind,
                    "resource_id": resource_id,
                    "resource_kind": resource_kind,
                    "role": role,
                    "attribute_id": attribute_id,
                    "context": context,
                    "tag_reference_id": tag_reference_id,
                },
                permission_create_all_params.PermissionCreateAllParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionCreateAllResponse,
        )

    def request(
        self,
        id: str,
        *,
        hub_id: str,
        type: Literal["project", "process", "table", "view"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Request permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not type:
            raise ValueError(f"Expected a non-empty value for `type` but received {type!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/v1/permissions/request/{hub_id}/{type}/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_tag(
        self,
        *,
        tag_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionRetrieveTagResponse:
        """
        Retrieve a tag by its public ID.

        Args:
          tag_id: Public ID of the tag to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/permissions/tag",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"tag_id": tag_id}, permission_retrieve_tag_params.PermissionRetrieveTagParams),
            ),
            cast_to=PermissionRetrieveTagResponse,
        )


class AsyncPermissionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPermissionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPermissionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPermissionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncPermissionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        attribute_kind: Literal["user", "tag", "project", "all_table_tags"],
        resource_id: str,
        resource_kind: Literal["process", "table", "table_view"],
        role: Literal[0, 1, 2, 3, 4],
        attribute_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        tag_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionCreateResponse:
        """
        Create permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/permissions",
            body=await async_maybe_transform(
                {
                    "attribute_kind": attribute_kind,
                    "resource_id": resource_id,
                    "resource_kind": resource_kind,
                    "role": role,
                    "attribute_id": attribute_id,
                    "context": context,
                    "tag_reference_id": tag_reference_id,
                },
                permission_create_params.PermissionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionCreateResponse,
        )

    async def retrieve(
        self,
        *,
        resource: Literal["process", "table", "table_view"],
        resource_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionRetrieveResponse:
        """
        Retrieve permissions for a specified resource, such as a table, table view, or
        process.

        Args:
          resource: The kind of resource for which to retrieve permissions. Valid options are
              'process', 'table', or 'table_view'.

          resource_id: UUID of the resource for which to retrieve permissions.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/permissions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "resource": resource,
                        "resource_id": resource_id,
                    },
                    permission_retrieve_params.PermissionRetrieveParams,
                ),
            ),
            cast_to=PermissionRetrieveResponse,
        )

    async def update(
        self,
        id: str,
        *,
        role: Literal[0, 1, 2, 3, 4],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionUpdateResponse:
        """
        Update permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/v1/permissions/{id}",
            body=await async_maybe_transform(
                {
                    "role": role,
                    "context": context,
                },
                permission_update_params.PermissionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionUpdateResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/permissions/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def create_all(
        self,
        *,
        attribute_kind: Literal["user", "tag", "project", "all_table_tags"],
        resource_id: str,
        resource_kind: Literal["process", "table", "table_view"],
        role: Literal[0, 1, 2, 3, 4],
        attribute_id: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        tag_reference_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionCreateAllResponse:
        """
        Create permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/permissions/all",
            body=await async_maybe_transform(
                {
                    "attribute_kind": attribute_kind,
                    "resource_id": resource_id,
                    "resource_kind": resource_kind,
                    "role": role,
                    "attribute_id": attribute_id,
                    "context": context,
                    "tag_reference_id": tag_reference_id,
                },
                permission_create_all_params.PermissionCreateAllParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PermissionCreateAllResponse,
        )

    async def request(
        self,
        id: str,
        *,
        hub_id: str,
        type: Literal["project", "process", "table", "view"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Request permissions for a specific resource (such as a table, table view, or
        process).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not type:
            raise ValueError(f"Expected a non-empty value for `type` but received {type!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/v1/permissions/request/{hub_id}/{type}/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_tag(
        self,
        *,
        tag_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PermissionRetrieveTagResponse:
        """
        Retrieve a tag by its public ID.

        Args:
          tag_id: Public ID of the tag to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/permissions/tag",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"tag_id": tag_id}, permission_retrieve_tag_params.PermissionRetrieveTagParams
                ),
            ),
            cast_to=PermissionRetrieveTagResponse,
        )


class PermissionsResourceWithRawResponse:
    def __init__(self, permissions: PermissionsResource) -> None:
        self._permissions = permissions

        self.create = to_raw_response_wrapper(
            permissions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            permissions.retrieve,
        )
        self.update = to_raw_response_wrapper(
            permissions.update,
        )
        self.delete = to_raw_response_wrapper(
            permissions.delete,
        )
        self.create_all = to_raw_response_wrapper(
            permissions.create_all,
        )
        self.request = to_raw_response_wrapper(
            permissions.request,
        )
        self.retrieve_tag = to_raw_response_wrapper(
            permissions.retrieve_tag,
        )


class AsyncPermissionsResourceWithRawResponse:
    def __init__(self, permissions: AsyncPermissionsResource) -> None:
        self._permissions = permissions

        self.create = async_to_raw_response_wrapper(
            permissions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            permissions.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            permissions.update,
        )
        self.delete = async_to_raw_response_wrapper(
            permissions.delete,
        )
        self.create_all = async_to_raw_response_wrapper(
            permissions.create_all,
        )
        self.request = async_to_raw_response_wrapper(
            permissions.request,
        )
        self.retrieve_tag = async_to_raw_response_wrapper(
            permissions.retrieve_tag,
        )


class PermissionsResourceWithStreamingResponse:
    def __init__(self, permissions: PermissionsResource) -> None:
        self._permissions = permissions

        self.create = to_streamed_response_wrapper(
            permissions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            permissions.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            permissions.update,
        )
        self.delete = to_streamed_response_wrapper(
            permissions.delete,
        )
        self.create_all = to_streamed_response_wrapper(
            permissions.create_all,
        )
        self.request = to_streamed_response_wrapper(
            permissions.request,
        )
        self.retrieve_tag = to_streamed_response_wrapper(
            permissions.retrieve_tag,
        )


class AsyncPermissionsResourceWithStreamingResponse:
    def __init__(self, permissions: AsyncPermissionsResource) -> None:
        self._permissions = permissions

        self.create = async_to_streamed_response_wrapper(
            permissions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            permissions.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            permissions.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            permissions.delete,
        )
        self.create_all = async_to_streamed_response_wrapper(
            permissions.create_all,
        )
        self.request = async_to_streamed_response_wrapper(
            permissions.request,
        )
        self.retrieve_tag = async_to_streamed_response_wrapper(
            permissions.retrieve_tag,
        )
