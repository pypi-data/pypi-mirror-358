# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import notification_create_params, notification_update_params, notification_list_events_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
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
from ..types.notification_create_response import NotificationCreateResponse
from ..types.notification_delete_response import NotificationDeleteResponse
from ..types.notification_update_response import NotificationUpdateResponse
from ..types.notification_list_events_response import NotificationListEventsResponse
from ..types.notification_list_event_types_response import NotificationListEventTypesResponse
from ..types.create_notification_schema_header_param import CreateNotificationSchemaHeaderParam

__all__ = ["NotificationsResource", "AsyncNotificationsResource"]


class NotificationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> NotificationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return NotificationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> NotificationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return NotificationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: str,
        project_id: str,
        triggers: Iterable[notification_create_params.Trigger],
        webhook_url: str,
        custom_headers: Iterable[CreateNotificationSchemaHeaderParam] | NotGiven = NOT_GIVEN,
        processes: List[str] | NotGiven = NOT_GIVEN,
        tables: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationCreateResponse:
        """
        Create a new notification for a specific hub.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/notifications",
            body=maybe_transform(
                {
                    "description": description,
                    "project_id": project_id,
                    "triggers": triggers,
                    "webhook_url": webhook_url,
                    "custom_headers": custom_headers,
                    "processes": processes,
                    "tables": tables,
                },
                notification_create_params.NotificationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationCreateResponse,
        )

    def update(
        self,
        id: str,
        *,
        webhook_url: str,
        custom_headers: Iterable[CreateNotificationSchemaHeaderParam] | NotGiven = NOT_GIVEN,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        processes: List[str] | NotGiven = NOT_GIVEN,
        tables: List[str] | NotGiven = NOT_GIVEN,
        triggers: Iterable[notification_update_params.Trigger] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationUpdateResponse:
        """
        Update a specific notification by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/v1/notifications/{id}",
            body=maybe_transform(
                {
                    "webhook_url": webhook_url,
                    "custom_headers": custom_headers,
                    "description": description,
                    "processes": processes,
                    "tables": tables,
                    "triggers": triggers,
                },
                notification_update_params.NotificationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationUpdateResponse,
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
    ) -> NotificationDeleteResponse:
        """
        Delete a specific notification by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._delete(
            f"/v1/notifications/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationDeleteResponse,
        )

    def list_event_types(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationListEventTypesResponse:
        """Retrieve a list of all supported event types for notifications."""
        return self._get(
            "/v1/notifications/event-types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationListEventTypesResponse,
        )

    def list_events(
        self,
        resource_id: str,
        *,
        type: Literal["process", "process_section", "process_response", "table", "project", "user"],
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        users: List[str] | NotGiven = NOT_GIVEN,
        verb: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationListEventsResponse:
        """
        Retrieve all events associated with a specific resource, filtered by various
        criteria.

        Args:
          type: The type of the resource (e.g., user, process, table, project).

          end_date: Optional end date to filter the events.

          page: Page number for pagination.

          search: Optional search term to filter the events.

          start_date: Optional start date to filter the events.

          users: Optional UUID of a user to filter the events.

          verb: Optional list of verbs to filter the events.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return self._get(
            f"/v1/notifications/events/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "type": type,
                        "end_date": end_date,
                        "page": page,
                        "search": search,
                        "start_date": start_date,
                        "users": users,
                        "verb": verb,
                    },
                    notification_list_events_params.NotificationListEventsParams,
                ),
            ),
            cast_to=NotificationListEventsResponse,
        )


class AsyncNotificationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncNotificationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncNotificationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncNotificationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncNotificationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: str,
        project_id: str,
        triggers: Iterable[notification_create_params.Trigger],
        webhook_url: str,
        custom_headers: Iterable[CreateNotificationSchemaHeaderParam] | NotGiven = NOT_GIVEN,
        processes: List[str] | NotGiven = NOT_GIVEN,
        tables: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationCreateResponse:
        """
        Create a new notification for a specific hub.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/notifications",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "project_id": project_id,
                    "triggers": triggers,
                    "webhook_url": webhook_url,
                    "custom_headers": custom_headers,
                    "processes": processes,
                    "tables": tables,
                },
                notification_create_params.NotificationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationCreateResponse,
        )

    async def update(
        self,
        id: str,
        *,
        webhook_url: str,
        custom_headers: Iterable[CreateNotificationSchemaHeaderParam] | NotGiven = NOT_GIVEN,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        processes: List[str] | NotGiven = NOT_GIVEN,
        tables: List[str] | NotGiven = NOT_GIVEN,
        triggers: Iterable[notification_update_params.Trigger] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationUpdateResponse:
        """
        Update a specific notification by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/v1/notifications/{id}",
            body=await async_maybe_transform(
                {
                    "webhook_url": webhook_url,
                    "custom_headers": custom_headers,
                    "description": description,
                    "processes": processes,
                    "tables": tables,
                    "triggers": triggers,
                },
                notification_update_params.NotificationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationUpdateResponse,
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
    ) -> NotificationDeleteResponse:
        """
        Delete a specific notification by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._delete(
            f"/v1/notifications/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationDeleteResponse,
        )

    async def list_event_types(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationListEventTypesResponse:
        """Retrieve a list of all supported event types for notifications."""
        return await self._get(
            "/v1/notifications/event-types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NotificationListEventTypesResponse,
        )

    async def list_events(
        self,
        resource_id: str,
        *,
        type: Literal["process", "process_section", "process_response", "table", "project", "user"],
        end_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        search: str | NotGiven = NOT_GIVEN,
        start_date: Union[str, datetime] | NotGiven = NOT_GIVEN,
        users: List[str] | NotGiven = NOT_GIVEN,
        verb: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> NotificationListEventsResponse:
        """
        Retrieve all events associated with a specific resource, filtered by various
        criteria.

        Args:
          type: The type of the resource (e.g., user, process, table, project).

          end_date: Optional end date to filter the events.

          page: Page number for pagination.

          search: Optional search term to filter the events.

          start_date: Optional start date to filter the events.

          users: Optional UUID of a user to filter the events.

          verb: Optional list of verbs to filter the events.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not resource_id:
            raise ValueError(f"Expected a non-empty value for `resource_id` but received {resource_id!r}")
        return await self._get(
            f"/v1/notifications/events/{resource_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "type": type,
                        "end_date": end_date,
                        "page": page,
                        "search": search,
                        "start_date": start_date,
                        "users": users,
                        "verb": verb,
                    },
                    notification_list_events_params.NotificationListEventsParams,
                ),
            ),
            cast_to=NotificationListEventsResponse,
        )


class NotificationsResourceWithRawResponse:
    def __init__(self, notifications: NotificationsResource) -> None:
        self._notifications = notifications

        self.create = to_raw_response_wrapper(
            notifications.create,
        )
        self.update = to_raw_response_wrapper(
            notifications.update,
        )
        self.delete = to_raw_response_wrapper(
            notifications.delete,
        )
        self.list_event_types = to_raw_response_wrapper(
            notifications.list_event_types,
        )
        self.list_events = to_raw_response_wrapper(
            notifications.list_events,
        )


class AsyncNotificationsResourceWithRawResponse:
    def __init__(self, notifications: AsyncNotificationsResource) -> None:
        self._notifications = notifications

        self.create = async_to_raw_response_wrapper(
            notifications.create,
        )
        self.update = async_to_raw_response_wrapper(
            notifications.update,
        )
        self.delete = async_to_raw_response_wrapper(
            notifications.delete,
        )
        self.list_event_types = async_to_raw_response_wrapper(
            notifications.list_event_types,
        )
        self.list_events = async_to_raw_response_wrapper(
            notifications.list_events,
        )


class NotificationsResourceWithStreamingResponse:
    def __init__(self, notifications: NotificationsResource) -> None:
        self._notifications = notifications

        self.create = to_streamed_response_wrapper(
            notifications.create,
        )
        self.update = to_streamed_response_wrapper(
            notifications.update,
        )
        self.delete = to_streamed_response_wrapper(
            notifications.delete,
        )
        self.list_event_types = to_streamed_response_wrapper(
            notifications.list_event_types,
        )
        self.list_events = to_streamed_response_wrapper(
            notifications.list_events,
        )


class AsyncNotificationsResourceWithStreamingResponse:
    def __init__(self, notifications: AsyncNotificationsResource) -> None:
        self._notifications = notifications

        self.create = async_to_streamed_response_wrapper(
            notifications.create,
        )
        self.update = async_to_streamed_response_wrapper(
            notifications.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            notifications.delete,
        )
        self.list_event_types = async_to_streamed_response_wrapper(
            notifications.list_event_types,
        )
        self.list_events = async_to_streamed_response_wrapper(
            notifications.list_events,
        )
