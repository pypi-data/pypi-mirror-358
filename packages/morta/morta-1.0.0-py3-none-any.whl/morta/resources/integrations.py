# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ..types import (
    integration_create_passthrough_params,
    integration_create_passthrough_download_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.base_request_context_param import BaseRequestContextParam
from ..types.integration_create_passthrough_response import IntegrationCreatePassthroughResponse

__all__ = ["IntegrationsResource", "AsyncIntegrationsResource"]


class IntegrationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IntegrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return IntegrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IntegrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return IntegrationsResourceWithStreamingResponse(self)

    def create_passthrough(
        self,
        *,
        method: Literal["GET", "PUT", "POST", "DELETE", "PATCH"],
        path: str,
        source_system: Literal["viewpoint", "aconex", "autodesk-bim360", "procore", "revizto", "morta", "asite"],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        data: object | NotGiven = NOT_GIVEN,
        headers: object | NotGiven = NOT_GIVEN,
        on_behalf_user_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IntegrationCreatePassthroughResponse:
        """
        Make a passthrough API call to an external source system.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/integrations/passthrough",
            body=maybe_transform(
                {
                    "method": method,
                    "path": path,
                    "source_system": source_system,
                    "context": context,
                    "data": data,
                    "headers": headers,
                    "on_behalf_user_id": on_behalf_user_id,
                },
                integration_create_passthrough_params.IntegrationCreatePassthroughParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IntegrationCreatePassthroughResponse,
        )

    def create_passthrough_download(
        self,
        *,
        method: Literal["GET", "PUT", "POST", "DELETE", "PATCH"],
        path: str,
        source_system: Literal["viewpoint", "aconex", "autodesk-bim360", "procore", "revizto", "morta", "asite"],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        data: object | NotGiven = NOT_GIVEN,
        headers: object | NotGiven = NOT_GIVEN,
        on_behalf_user_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Make a passthrough API call to an external source system for downloading files.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._post(
            "/v1/integrations/passthrough-download",
            body=maybe_transform(
                {
                    "method": method,
                    "path": path,
                    "source_system": source_system,
                    "context": context,
                    "data": data,
                    "headers": headers,
                    "on_behalf_user_id": on_behalf_user_id,
                },
                integration_create_passthrough_download_params.IntegrationCreatePassthroughDownloadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncIntegrationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIntegrationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIntegrationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIntegrationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncIntegrationsResourceWithStreamingResponse(self)

    async def create_passthrough(
        self,
        *,
        method: Literal["GET", "PUT", "POST", "DELETE", "PATCH"],
        path: str,
        source_system: Literal["viewpoint", "aconex", "autodesk-bim360", "procore", "revizto", "morta", "asite"],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        data: object | NotGiven = NOT_GIVEN,
        headers: object | NotGiven = NOT_GIVEN,
        on_behalf_user_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IntegrationCreatePassthroughResponse:
        """
        Make a passthrough API call to an external source system.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/integrations/passthrough",
            body=await async_maybe_transform(
                {
                    "method": method,
                    "path": path,
                    "source_system": source_system,
                    "context": context,
                    "data": data,
                    "headers": headers,
                    "on_behalf_user_id": on_behalf_user_id,
                },
                integration_create_passthrough_params.IntegrationCreatePassthroughParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IntegrationCreatePassthroughResponse,
        )

    async def create_passthrough_download(
        self,
        *,
        method: Literal["GET", "PUT", "POST", "DELETE", "PATCH"],
        path: str,
        source_system: Literal["viewpoint", "aconex", "autodesk-bim360", "procore", "revizto", "morta", "asite"],
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        data: object | NotGiven = NOT_GIVEN,
        headers: object | NotGiven = NOT_GIVEN,
        on_behalf_user_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Make a passthrough API call to an external source system for downloading files.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._post(
            "/v1/integrations/passthrough-download",
            body=await async_maybe_transform(
                {
                    "method": method,
                    "path": path,
                    "source_system": source_system,
                    "context": context,
                    "data": data,
                    "headers": headers,
                    "on_behalf_user_id": on_behalf_user_id,
                },
                integration_create_passthrough_download_params.IntegrationCreatePassthroughDownloadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class IntegrationsResourceWithRawResponse:
    def __init__(self, integrations: IntegrationsResource) -> None:
        self._integrations = integrations

        self.create_passthrough = to_raw_response_wrapper(
            integrations.create_passthrough,
        )
        self.create_passthrough_download = to_custom_raw_response_wrapper(
            integrations.create_passthrough_download,
            BinaryAPIResponse,
        )


class AsyncIntegrationsResourceWithRawResponse:
    def __init__(self, integrations: AsyncIntegrationsResource) -> None:
        self._integrations = integrations

        self.create_passthrough = async_to_raw_response_wrapper(
            integrations.create_passthrough,
        )
        self.create_passthrough_download = async_to_custom_raw_response_wrapper(
            integrations.create_passthrough_download,
            AsyncBinaryAPIResponse,
        )


class IntegrationsResourceWithStreamingResponse:
    def __init__(self, integrations: IntegrationsResource) -> None:
        self._integrations = integrations

        self.create_passthrough = to_streamed_response_wrapper(
            integrations.create_passthrough,
        )
        self.create_passthrough_download = to_custom_streamed_response_wrapper(
            integrations.create_passthrough_download,
            StreamedBinaryAPIResponse,
        )


class AsyncIntegrationsResourceWithStreamingResponse:
    def __init__(self, integrations: AsyncIntegrationsResource) -> None:
        self._integrations = integrations

        self.create_passthrough = async_to_streamed_response_wrapper(
            integrations.create_passthrough,
        )
        self.create_passthrough_download = async_to_custom_streamed_response_wrapper(
            integrations.create_passthrough_download,
            AsyncStreamedBinaryAPIResponse,
        )
