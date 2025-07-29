# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import permissions, integrations, notifications
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import MortaError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.hub import hub
from .resources.user import user
from .resources.table import table
from .resources.document import document
from .resources.comment_thread import comment_thread

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Morta", "AsyncMorta", "Client", "AsyncClient"]


class Morta(SyncAPIClient):
    user: user.UserResource
    hub: hub.HubResource
    table: table.TableResource
    document: document.DocumentResource
    notifications: notifications.NotificationsResource
    comment_thread: comment_thread.CommentThreadResource
    permissions: permissions.PermissionsResource
    integrations: integrations.IntegrationsResource
    with_raw_response: MortaWithRawResponse
    with_streaming_response: MortaWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Morta client instance.

        This automatically infers the `api_key` argument from the `MORTA_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("MORTA_API_KEY")
        if api_key is None:
            raise MortaError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MORTA_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("MORTA_BASE_URL")
        if base_url is None:
            base_url = f"https://api.morta.io"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.user = user.UserResource(self)
        self.hub = hub.HubResource(self)
        self.table = table.TableResource(self)
        self.document = document.DocumentResource(self)
        self.notifications = notifications.NotificationsResource(self)
        self.comment_thread = comment_thread.CommentThreadResource(self)
        self.permissions = permissions.PermissionsResource(self)
        self.integrations = integrations.IntegrationsResource(self)
        self.with_raw_response = MortaWithRawResponse(self)
        self.with_streaming_response = MortaWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncMorta(AsyncAPIClient):
    user: user.AsyncUserResource
    hub: hub.AsyncHubResource
    table: table.AsyncTableResource
    document: document.AsyncDocumentResource
    notifications: notifications.AsyncNotificationsResource
    comment_thread: comment_thread.AsyncCommentThreadResource
    permissions: permissions.AsyncPermissionsResource
    integrations: integrations.AsyncIntegrationsResource
    with_raw_response: AsyncMortaWithRawResponse
    with_streaming_response: AsyncMortaWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncMorta client instance.

        This automatically infers the `api_key` argument from the `MORTA_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("MORTA_API_KEY")
        if api_key is None:
            raise MortaError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MORTA_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("MORTA_BASE_URL")
        if base_url is None:
            base_url = f"https://api.morta.io"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.user = user.AsyncUserResource(self)
        self.hub = hub.AsyncHubResource(self)
        self.table = table.AsyncTableResource(self)
        self.document = document.AsyncDocumentResource(self)
        self.notifications = notifications.AsyncNotificationsResource(self)
        self.comment_thread = comment_thread.AsyncCommentThreadResource(self)
        self.permissions = permissions.AsyncPermissionsResource(self)
        self.integrations = integrations.AsyncIntegrationsResource(self)
        self.with_raw_response = AsyncMortaWithRawResponse(self)
        self.with_streaming_response = AsyncMortaWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class MortaWithRawResponse:
    def __init__(self, client: Morta) -> None:
        self.user = user.UserResourceWithRawResponse(client.user)
        self.hub = hub.HubResourceWithRawResponse(client.hub)
        self.table = table.TableResourceWithRawResponse(client.table)
        self.document = document.DocumentResourceWithRawResponse(client.document)
        self.notifications = notifications.NotificationsResourceWithRawResponse(client.notifications)
        self.comment_thread = comment_thread.CommentThreadResourceWithRawResponse(client.comment_thread)
        self.permissions = permissions.PermissionsResourceWithRawResponse(client.permissions)
        self.integrations = integrations.IntegrationsResourceWithRawResponse(client.integrations)


class AsyncMortaWithRawResponse:
    def __init__(self, client: AsyncMorta) -> None:
        self.user = user.AsyncUserResourceWithRawResponse(client.user)
        self.hub = hub.AsyncHubResourceWithRawResponse(client.hub)
        self.table = table.AsyncTableResourceWithRawResponse(client.table)
        self.document = document.AsyncDocumentResourceWithRawResponse(client.document)
        self.notifications = notifications.AsyncNotificationsResourceWithRawResponse(client.notifications)
        self.comment_thread = comment_thread.AsyncCommentThreadResourceWithRawResponse(client.comment_thread)
        self.permissions = permissions.AsyncPermissionsResourceWithRawResponse(client.permissions)
        self.integrations = integrations.AsyncIntegrationsResourceWithRawResponse(client.integrations)


class MortaWithStreamedResponse:
    def __init__(self, client: Morta) -> None:
        self.user = user.UserResourceWithStreamingResponse(client.user)
        self.hub = hub.HubResourceWithStreamingResponse(client.hub)
        self.table = table.TableResourceWithStreamingResponse(client.table)
        self.document = document.DocumentResourceWithStreamingResponse(client.document)
        self.notifications = notifications.NotificationsResourceWithStreamingResponse(client.notifications)
        self.comment_thread = comment_thread.CommentThreadResourceWithStreamingResponse(client.comment_thread)
        self.permissions = permissions.PermissionsResourceWithStreamingResponse(client.permissions)
        self.integrations = integrations.IntegrationsResourceWithStreamingResponse(client.integrations)


class AsyncMortaWithStreamedResponse:
    def __init__(self, client: AsyncMorta) -> None:
        self.user = user.AsyncUserResourceWithStreamingResponse(client.user)
        self.hub = hub.AsyncHubResourceWithStreamingResponse(client.hub)
        self.table = table.AsyncTableResourceWithStreamingResponse(client.table)
        self.document = document.AsyncDocumentResourceWithStreamingResponse(client.document)
        self.notifications = notifications.AsyncNotificationsResourceWithStreamingResponse(client.notifications)
        self.comment_thread = comment_thread.AsyncCommentThreadResourceWithStreamingResponse(client.comment_thread)
        self.permissions = permissions.AsyncPermissionsResourceWithStreamingResponse(client.permissions)
        self.integrations = integrations.AsyncIntegrationsResourceWithStreamingResponse(client.integrations)


Client = Morta

AsyncClient = AsyncMorta
