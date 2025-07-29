# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Mapping, Optional, cast
from typing_extensions import Literal

import httpx

from .invite import (
    InviteResource,
    AsyncInviteResource,
    InviteResourceWithRawResponse,
    AsyncInviteResourceWithRawResponse,
    InviteResourceWithStreamingResponse,
    AsyncInviteResourceWithStreamingResponse,
)
from ...types import (
    hub_create_params,
    hub_update_params,
    hub_ai_search_params,
    hub_duplicate_params,
    hub_get_resources_params,
    hub_upload_template_params,
    hub_change_user_role_params,
    hub_search_resources_params,
    hub_create_knowledge_base_params,
    hub_invite_multiple_users_params,
    hub_get_sent_notifications_params,
    hub_update_heading_styling_params,
)
from .secrets import (
    SecretsResource,
    AsyncSecretsResource,
    SecretsResourceWithRawResponse,
    AsyncSecretsResourceWithRawResponse,
    SecretsResourceWithStreamingResponse,
    AsyncSecretsResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, FileTypes
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from .ai_answer import (
    AIAnswerResource,
    AsyncAIAnswerResource,
    AIAnswerResourceWithRawResponse,
    AsyncAIAnswerResourceWithRawResponse,
    AIAnswerResourceWithStreamingResponse,
    AsyncAIAnswerResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.hub_create_response import HubCreateResponse
from ...types.hub_delete_response import HubDeleteResponse
from ...types.hub_update_response import HubUpdateResponse
from ...types.hub_restore_response import HubRestoreResponse
from ...types.hub_get_tags_response import HubGetTagsResponse
from ...types.hub_retrieve_response import HubRetrieveResponse
from ...types.hub_ai_search_response import HubAISearchResponse
from ...types.hub_get_tables_response import HubGetTablesResponse
from ...types.hub_get_members_response import HubGetMembersResponse
from ...types.hub_remove_user_response import HubRemoveUserResponse
from ...types.base_request_context_param import BaseRequestContextParam
from ...types.hub_get_documents_response import HubGetDocumentsResponse
from ...types.hub_get_resources_response import HubGetResourcesResponse
from ...types.hub_get_variables_response import HubGetVariablesResponse
from ...types.hub_get_ai_answers_response import HubGetAIAnswersResponse
from ...types.hub_upload_template_response import HubUploadTemplateResponse
from ...types.hub_change_user_role_response import HubChangeUserRoleResponse
from ...types.hub_search_resources_response import HubSearchResourcesResponse
from ...types.hub_get_notifications_response import HubGetNotificationsResponse
from ...types.hub_get_deleted_tables_response import HubGetDeletedTablesResponse
from ...types.hub_permanently_delete_response import HubPermanentlyDeleteResponse
from ...types.hub_get_invited_members_response import HubGetInvitedMembersResponse
from ...types.hub_get_deleted_documents_response import HubGetDeletedDocumentsResponse
from ...types.hub_invite_multiple_users_response import HubInviteMultipleUsersResponse
from ...types.hub_create_heading_styling_response import HubCreateHeadingStylingResponse
from ...types.hub_get_sent_notifications_response import HubGetSentNotificationsResponse
from ...types.hub_update_heading_styling_response import HubUpdateHeadingStylingResponse
from ...types.hub_get_duplicated_children_response import HubGetDuplicatedChildrenResponse
from ...types.hub_delete_top_heading_styling_response import HubDeleteTopHeadingStylingResponse

__all__ = ["HubResource", "AsyncHubResource"]


class HubResource(SyncAPIResource):
    @cached_property
    def ai_answer(self) -> AIAnswerResource:
        return AIAnswerResource(self._client)

    @cached_property
    def invite(self) -> InviteResource:
        return InviteResource(self._client)

    @cached_property
    def secrets(self) -> SecretsResource:
        return SecretsResource(self._client)

    @cached_property
    def with_raw_response(self) -> HubResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return HubResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HubResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return HubResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubCreateResponse:
        """
        Create a new hub with the specified name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/hub",
            body=maybe_transform({"name": name}, hub_create_params.HubCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubCreateResponse,
        )

    def retrieve(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubRetrieveResponse:
        """
        Retrieve detailed information about a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubRetrieveResponse,
        )

    def update(
        self,
        hub_id: str,
        *,
        ai_search_enabled: Optional[bool] | NotGiven = NOT_GIVEN,
        allow_document_export: Optional[bool] | NotGiven = NOT_GIVEN,
        allow_table_export: Optional[bool] | NotGiven = NOT_GIVEN,
        bulk_update_text: hub_update_params.BulkUpdateText | NotGiven = NOT_GIVEN,
        default_banner: Optional[str] | NotGiven = NOT_GIVEN,
        default_date_format: Optional[str] | NotGiven = NOT_GIVEN,
        default_datetime_format: Optional[str] | NotGiven = NOT_GIVEN,
        default_header_background_color: Optional[str] | NotGiven = NOT_GIVEN,
        default_header_text_color: Optional[str] | NotGiven = NOT_GIVEN,
        default_process_id: Optional[str] | NotGiven = NOT_GIVEN,
        domains_access: Optional[List[str]] | NotGiven = NOT_GIVEN,
        font_colour: Optional[str] | NotGiven = NOT_GIVEN,
        hide_process_created: Optional[bool] | NotGiven = NOT_GIVEN,
        logo: Optional[str] | NotGiven = NOT_GIVEN,
        mfa_required: Optional[bool] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        primary_colour: Optional[str] | NotGiven = NOT_GIVEN,
        process_title_alignment: Optional[Literal["left", "center", "right"]] | NotGiven = NOT_GIVEN,
        process_title_bold: Optional[bool] | NotGiven = NOT_GIVEN,
        process_title_colour: Optional[str] | NotGiven = NOT_GIVEN,
        process_title_font_size: Optional[float] | NotGiven = NOT_GIVEN,
        process_title_italic: Optional[bool] | NotGiven = NOT_GIVEN,
        process_title_underline: Optional[bool] | NotGiven = NOT_GIVEN,
        public: Optional[bool] | NotGiven = NOT_GIVEN,
        word_template: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubUpdateResponse:
        """
        Update an existing hub's details by hub ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._put(
            f"/v1/hub/{hub_id}",
            body=maybe_transform(
                {
                    "ai_search_enabled": ai_search_enabled,
                    "allow_document_export": allow_document_export,
                    "allow_table_export": allow_table_export,
                    "bulk_update_text": bulk_update_text,
                    "default_banner": default_banner,
                    "default_date_format": default_date_format,
                    "default_datetime_format": default_datetime_format,
                    "default_header_background_color": default_header_background_color,
                    "default_header_text_color": default_header_text_color,
                    "default_process_id": default_process_id,
                    "domains_access": domains_access,
                    "font_colour": font_colour,
                    "hide_process_created": hide_process_created,
                    "logo": logo,
                    "mfa_required": mfa_required,
                    "name": name,
                    "primary_colour": primary_colour,
                    "process_title_alignment": process_title_alignment,
                    "process_title_bold": process_title_bold,
                    "process_title_colour": process_title_colour,
                    "process_title_font_size": process_title_font_size,
                    "process_title_italic": process_title_italic,
                    "process_title_underline": process_title_underline,
                    "public": public,
                    "word_template": word_template,
                },
                hub_update_params.HubUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubUpdateResponse,
        )

    def delete(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubDeleteResponse:
        """
        Delete a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._delete(
            f"/v1/hub/{hub_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubDeleteResponse,
        )

    def ai_search(
        self,
        hub_id: str,
        *,
        search: str,
        process_public_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubAISearchResponse:
        """
        Perform an AI search operation within a specific hub, identified by its UUID

        Args:
          search: Search query string

          process_public_id: Optional UUID of a document to restrict the search within a specific document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/search-ai",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "search": search,
                        "process_public_id": process_public_id,
                    },
                    hub_ai_search_params.HubAISearchParams,
                ),
            ),
            cast_to=HubAISearchResponse,
        )

    def change_user_role(
        self,
        firebase_id: str,
        *,
        hub_id: str,
        role: Literal["owner", "admin", "member"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubChangeUserRoleResponse:
        """
        Change the role of a user in a specific hub, identified by the hub's UUID and
        user's Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._put(
            f"/v1/hub/{hub_id}/change-user-role/{firebase_id}",
            body=maybe_transform({"role": role}, hub_change_user_role_params.HubChangeUserRoleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubChangeUserRoleResponse,
        )

    def create_heading_styling(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubCreateHeadingStylingResponse:
        """
        Create new heading styling for a specific hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._post(
            f"/v1/hub/{hub_id}/add_heading_styling",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubCreateHeadingStylingResponse,
        )

    def create_knowledge_base(
        self,
        hub_id: str,
        *,
        source: str,
        text: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        link: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new knowledge base entry for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/knowledge-base",
            body=maybe_transform(
                {
                    "source": source,
                    "text": text,
                    "context": context,
                    "link": link,
                },
                hub_create_knowledge_base_params.HubCreateKnowledgeBaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def delete_top_heading_styling(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubDeleteTopHeadingStylingResponse:
        """
        Delete the top heading styling for a specific hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._delete(
            f"/v1/hub/{hub_id}/delete_top_style",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubDeleteTopHeadingStylingResponse,
        )

    def duplicate(
        self,
        hub_id: str,
        *,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        duplicate_permissions: bool | NotGiven = NOT_GIVEN,
        lock_resource: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a duplicate of an existing hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/duplicate",
            body=maybe_transform(
                {
                    "context": context,
                    "duplicate_permissions": duplicate_permissions,
                    "lock_resource": lock_resource,
                },
                hub_duplicate_params.HubDuplicateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_ai_answers(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetAIAnswersResponse:
        """
        Retrieve AI answers within a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/ai-answers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetAIAnswersResponse,
        )

    def get_deleted_documents(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDeletedDocumentsResponse:
        """
        Get all deleted documents associated with a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/deleted-documents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDeletedDocumentsResponse,
        )

    def get_deleted_tables(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDeletedTablesResponse:
        """Retrieve all deleted tables from a specific hub, identified by its UUID.

        Only
        accessible by hub owners.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/deleted-tables",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDeletedTablesResponse,
        )

    def get_documents(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDocumentsResponse:
        """
        Get all documents associated with a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/documents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDocumentsResponse,
        )

    def get_duplicated_children(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDuplicatedChildrenResponse:
        """
        Get duplicated children of a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/duplicated-children",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDuplicatedChildrenResponse,
        )

    def get_invited_members(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetInvitedMembersResponse:
        """
        Retrieve all invited members for a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/invited-members",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetInvitedMembersResponse,
        )

    def get_members(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetMembersResponse:
        """
        Retrieve all members associated with a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/members",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetMembersResponse,
        )

    def get_notifications(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetNotificationsResponse:
        """Retrieve all notifications associated with a specific hub.

        This endpoint is
        accessible only to users with owner-level permissions for the hub.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/notifications",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetNotificationsResponse,
        )

    def get_resources(
        self,
        hub_id: str,
        *,
        admin_view: Optional[bool] | NotGiven = NOT_GIVEN,
        exclude_processes: Optional[bool] | NotGiven = NOT_GIVEN,
        exclude_tables: Optional[bool] | NotGiven = NOT_GIVEN,
        only_admin: bool | NotGiven = NOT_GIVEN,
        only_deleted: Optional[bool] | NotGiven = NOT_GIVEN,
        project_permissions: Optional[bool] | NotGiven = NOT_GIVEN,
        type_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetResourcesResponse:
        """
        Retrieve resources associated with a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._post(
            f"/v1/hub/{hub_id}/resources",
            body=maybe_transform(
                {
                    "admin_view": admin_view,
                    "exclude_processes": exclude_processes,
                    "exclude_tables": exclude_tables,
                    "only_admin": only_admin,
                    "only_deleted": only_deleted,
                    "project_permissions": project_permissions,
                    "type_id": type_id,
                },
                hub_get_resources_params.HubGetResourcesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetResourcesResponse,
        )

    def get_sent_notifications(
        self,
        hub_id: str,
        *,
        notification_id: Optional[str] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetSentNotificationsResponse:
        """
        Retrieve all sent notifications for a specified hub

        Args:
          notification_id: UUID of a specific notification to filter the executions

          page: Page number of the notification executions

          size: Number of notification executions per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/sent-notifications",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "notification_id": notification_id,
                        "page": page,
                        "size": size,
                    },
                    hub_get_sent_notifications_params.HubGetSentNotificationsParams,
                ),
            ),
            cast_to=HubGetSentNotificationsResponse,
        )

    def get_tables(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetTablesResponse:
        """
        Retrieve tables associated with a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/tables",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetTablesResponse,
        )

    def get_tags(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetTagsResponse:
        """
        Retrieve all tags associated with a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/tags",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetTagsResponse,
        )

    def get_variables(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetVariablesResponse:
        """
        Retrieve all variables associated with a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/variables",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetVariablesResponse,
        )

    def invite_multiple_users(
        self,
        hub_id: str,
        *,
        emails: List[str] | NotGiven = NOT_GIVEN,
        project_role: Literal["member", "admin", "owner"] | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubInviteMultipleUsersResponse:
        """Invite multiple users to join a hub, by email.

        If users already exist, they are
        added directly, otherwise, an invite is sent. Requires owner or admin
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
            f"/v1/hub/{hub_id}/invite-multiple",
            body=maybe_transform(
                {
                    "emails": emails,
                    "project_role": project_role,
                    "tags": tags,
                },
                hub_invite_multiple_users_params.HubInviteMultipleUsersParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubInviteMultipleUsersResponse,
        )

    def permanently_delete(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubPermanentlyDeleteResponse:
        """
        Permanently delete a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._delete(
            f"/v1/hub/{hub_id}/permanent",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubPermanentlyDeleteResponse,
        )

    def remove_user(
        self,
        firebase_id: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubRemoveUserResponse:
        """
        Remove a user from a specific hub, identified by the hub's UUID and user's
        Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return self._delete(
            f"/v1/hub/{hub_id}/remove-user/{firebase_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubRemoveUserResponse,
        )

    def request_contributor_access(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Request contributor access to a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/request-contributor-access",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def restore(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubRestoreResponse:
        """
        Restore a specific hub, identified by its UUID, that has been previously deleted

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._put(
            f"/v1/hub/{hub_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubRestoreResponse,
        )

    def search_resources(
        self,
        hub_id: str,
        *,
        search: str,
        process_public_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubSearchResourcesResponse:
        """
        Perform a search operation within a specific hub, identified by its UUID

        Args:
          search: Search query string

          process_public_id: Optional UUID of a document to restrict the search within a specific document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return self._get(
            f"/v1/hub/{hub_id}/search-resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "search": search,
                        "process_public_id": process_public_id,
                    },
                    hub_search_resources_params.HubSearchResourcesParams,
                ),
            ),
            cast_to=HubSearchResourcesResponse,
        )

    def set_column_coloring(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Set column coloring for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/set-column-coloring",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def set_column_format(
        self,
        kind: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Set column date formatting for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not kind:
            raise ValueError(f"Expected a non-empty value for `kind` but received {kind!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/set-column-format/{kind}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def train_knowledge_base(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Train the knowledge base for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/train-knowledge-base",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update_heading_styling(
        self,
        style_id: str,
        *,
        hub_id: str,
        bold: bool | NotGiven = NOT_GIVEN,
        colour: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        font_size: float | NotGiven = NOT_GIVEN,
        italic: bool | NotGiven = NOT_GIVEN,
        numbering_style: int | NotGiven = NOT_GIVEN,
        start_at0: bool | NotGiven = NOT_GIVEN,
        underline: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubUpdateHeadingStylingResponse:
        """
        Update heading styling for a specific hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not style_id:
            raise ValueError(f"Expected a non-empty value for `style_id` but received {style_id!r}")
        return self._post(
            f"/v1/hub/{hub_id}/style/{style_id}",
            body=maybe_transform(
                {
                    "bold": bold,
                    "colour": colour,
                    "context": context,
                    "font_size": font_size,
                    "italic": italic,
                    "numbering_style": numbering_style,
                    "start_at0": start_at0,
                    "underline": underline,
                },
                hub_update_heading_styling_params.HubUpdateHeadingStylingParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubUpdateHeadingStylingResponse,
        )

    def upload_template(
        self,
        hub_id: str,
        *,
        file: FileTypes | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubUploadTemplateResponse:
        """
        Upload a template document for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/v1/hub/{hub_id}/upload-template",
            body=maybe_transform(body, hub_upload_template_params.HubUploadTemplateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubUploadTemplateResponse,
        )


class AsyncHubResource(AsyncAPIResource):
    @cached_property
    def ai_answer(self) -> AsyncAIAnswerResource:
        return AsyncAIAnswerResource(self._client)

    @cached_property
    def invite(self) -> AsyncInviteResource:
        return AsyncInviteResource(self._client)

    @cached_property
    def secrets(self) -> AsyncSecretsResource:
        return AsyncSecretsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncHubResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/morta-technology/morta-python#accessing-raw-response-data-eg-headers
        """
        return AsyncHubResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHubResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/morta-technology/morta-python#with_streaming_response
        """
        return AsyncHubResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubCreateResponse:
        """
        Create a new hub with the specified name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/hub",
            body=await async_maybe_transform({"name": name}, hub_create_params.HubCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubCreateResponse,
        )

    async def retrieve(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubRetrieveResponse:
        """
        Retrieve detailed information about a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubRetrieveResponse,
        )

    async def update(
        self,
        hub_id: str,
        *,
        ai_search_enabled: Optional[bool] | NotGiven = NOT_GIVEN,
        allow_document_export: Optional[bool] | NotGiven = NOT_GIVEN,
        allow_table_export: Optional[bool] | NotGiven = NOT_GIVEN,
        bulk_update_text: hub_update_params.BulkUpdateText | NotGiven = NOT_GIVEN,
        default_banner: Optional[str] | NotGiven = NOT_GIVEN,
        default_date_format: Optional[str] | NotGiven = NOT_GIVEN,
        default_datetime_format: Optional[str] | NotGiven = NOT_GIVEN,
        default_header_background_color: Optional[str] | NotGiven = NOT_GIVEN,
        default_header_text_color: Optional[str] | NotGiven = NOT_GIVEN,
        default_process_id: Optional[str] | NotGiven = NOT_GIVEN,
        domains_access: Optional[List[str]] | NotGiven = NOT_GIVEN,
        font_colour: Optional[str] | NotGiven = NOT_GIVEN,
        hide_process_created: Optional[bool] | NotGiven = NOT_GIVEN,
        logo: Optional[str] | NotGiven = NOT_GIVEN,
        mfa_required: Optional[bool] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        primary_colour: Optional[str] | NotGiven = NOT_GIVEN,
        process_title_alignment: Optional[Literal["left", "center", "right"]] | NotGiven = NOT_GIVEN,
        process_title_bold: Optional[bool] | NotGiven = NOT_GIVEN,
        process_title_colour: Optional[str] | NotGiven = NOT_GIVEN,
        process_title_font_size: Optional[float] | NotGiven = NOT_GIVEN,
        process_title_italic: Optional[bool] | NotGiven = NOT_GIVEN,
        process_title_underline: Optional[bool] | NotGiven = NOT_GIVEN,
        public: Optional[bool] | NotGiven = NOT_GIVEN,
        word_template: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubUpdateResponse:
        """
        Update an existing hub's details by hub ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._put(
            f"/v1/hub/{hub_id}",
            body=await async_maybe_transform(
                {
                    "ai_search_enabled": ai_search_enabled,
                    "allow_document_export": allow_document_export,
                    "allow_table_export": allow_table_export,
                    "bulk_update_text": bulk_update_text,
                    "default_banner": default_banner,
                    "default_date_format": default_date_format,
                    "default_datetime_format": default_datetime_format,
                    "default_header_background_color": default_header_background_color,
                    "default_header_text_color": default_header_text_color,
                    "default_process_id": default_process_id,
                    "domains_access": domains_access,
                    "font_colour": font_colour,
                    "hide_process_created": hide_process_created,
                    "logo": logo,
                    "mfa_required": mfa_required,
                    "name": name,
                    "primary_colour": primary_colour,
                    "process_title_alignment": process_title_alignment,
                    "process_title_bold": process_title_bold,
                    "process_title_colour": process_title_colour,
                    "process_title_font_size": process_title_font_size,
                    "process_title_italic": process_title_italic,
                    "process_title_underline": process_title_underline,
                    "public": public,
                    "word_template": word_template,
                },
                hub_update_params.HubUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubUpdateResponse,
        )

    async def delete(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubDeleteResponse:
        """
        Delete a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._delete(
            f"/v1/hub/{hub_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubDeleteResponse,
        )

    async def ai_search(
        self,
        hub_id: str,
        *,
        search: str,
        process_public_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubAISearchResponse:
        """
        Perform an AI search operation within a specific hub, identified by its UUID

        Args:
          search: Search query string

          process_public_id: Optional UUID of a document to restrict the search within a specific document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/search-ai",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "search": search,
                        "process_public_id": process_public_id,
                    },
                    hub_ai_search_params.HubAISearchParams,
                ),
            ),
            cast_to=HubAISearchResponse,
        )

    async def change_user_role(
        self,
        firebase_id: str,
        *,
        hub_id: str,
        role: Literal["owner", "admin", "member"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubChangeUserRoleResponse:
        """
        Change the role of a user in a specific hub, identified by the hub's UUID and
        user's Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._put(
            f"/v1/hub/{hub_id}/change-user-role/{firebase_id}",
            body=await async_maybe_transform({"role": role}, hub_change_user_role_params.HubChangeUserRoleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubChangeUserRoleResponse,
        )

    async def create_heading_styling(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubCreateHeadingStylingResponse:
        """
        Create new heading styling for a specific hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._post(
            f"/v1/hub/{hub_id}/add_heading_styling",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubCreateHeadingStylingResponse,
        )

    async def create_knowledge_base(
        self,
        hub_id: str,
        *,
        source: str,
        text: str,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        link: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a new knowledge base entry for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/knowledge-base",
            body=await async_maybe_transform(
                {
                    "source": source,
                    "text": text,
                    "context": context,
                    "link": link,
                },
                hub_create_knowledge_base_params.HubCreateKnowledgeBaseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete_top_heading_styling(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubDeleteTopHeadingStylingResponse:
        """
        Delete the top heading styling for a specific hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._delete(
            f"/v1/hub/{hub_id}/delete_top_style",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubDeleteTopHeadingStylingResponse,
        )

    async def duplicate(
        self,
        hub_id: str,
        *,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        duplicate_permissions: bool | NotGiven = NOT_GIVEN,
        lock_resource: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a duplicate of an existing hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/duplicate",
            body=await async_maybe_transform(
                {
                    "context": context,
                    "duplicate_permissions": duplicate_permissions,
                    "lock_resource": lock_resource,
                },
                hub_duplicate_params.HubDuplicateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_ai_answers(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetAIAnswersResponse:
        """
        Retrieve AI answers within a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/ai-answers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetAIAnswersResponse,
        )

    async def get_deleted_documents(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDeletedDocumentsResponse:
        """
        Get all deleted documents associated with a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/deleted-documents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDeletedDocumentsResponse,
        )

    async def get_deleted_tables(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDeletedTablesResponse:
        """Retrieve all deleted tables from a specific hub, identified by its UUID.

        Only
        accessible by hub owners.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/deleted-tables",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDeletedTablesResponse,
        )

    async def get_documents(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDocumentsResponse:
        """
        Get all documents associated with a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/documents",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDocumentsResponse,
        )

    async def get_duplicated_children(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetDuplicatedChildrenResponse:
        """
        Get duplicated children of a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/duplicated-children",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetDuplicatedChildrenResponse,
        )

    async def get_invited_members(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetInvitedMembersResponse:
        """
        Retrieve all invited members for a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/invited-members",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetInvitedMembersResponse,
        )

    async def get_members(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetMembersResponse:
        """
        Retrieve all members associated with a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/members",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetMembersResponse,
        )

    async def get_notifications(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetNotificationsResponse:
        """Retrieve all notifications associated with a specific hub.

        This endpoint is
        accessible only to users with owner-level permissions for the hub.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/notifications",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetNotificationsResponse,
        )

    async def get_resources(
        self,
        hub_id: str,
        *,
        admin_view: Optional[bool] | NotGiven = NOT_GIVEN,
        exclude_processes: Optional[bool] | NotGiven = NOT_GIVEN,
        exclude_tables: Optional[bool] | NotGiven = NOT_GIVEN,
        only_admin: bool | NotGiven = NOT_GIVEN,
        only_deleted: Optional[bool] | NotGiven = NOT_GIVEN,
        project_permissions: Optional[bool] | NotGiven = NOT_GIVEN,
        type_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetResourcesResponse:
        """
        Retrieve resources associated with a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._post(
            f"/v1/hub/{hub_id}/resources",
            body=await async_maybe_transform(
                {
                    "admin_view": admin_view,
                    "exclude_processes": exclude_processes,
                    "exclude_tables": exclude_tables,
                    "only_admin": only_admin,
                    "only_deleted": only_deleted,
                    "project_permissions": project_permissions,
                    "type_id": type_id,
                },
                hub_get_resources_params.HubGetResourcesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetResourcesResponse,
        )

    async def get_sent_notifications(
        self,
        hub_id: str,
        *,
        notification_id: Optional[str] | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        size: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetSentNotificationsResponse:
        """
        Retrieve all sent notifications for a specified hub

        Args:
          notification_id: UUID of a specific notification to filter the executions

          page: Page number of the notification executions

          size: Number of notification executions per page

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/sent-notifications",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "notification_id": notification_id,
                        "page": page,
                        "size": size,
                    },
                    hub_get_sent_notifications_params.HubGetSentNotificationsParams,
                ),
            ),
            cast_to=HubGetSentNotificationsResponse,
        )

    async def get_tables(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetTablesResponse:
        """
        Retrieve tables associated with a specific hub, identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/tables",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetTablesResponse,
        )

    async def get_tags(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetTagsResponse:
        """
        Retrieve all tags associated with a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/tags",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetTagsResponse,
        )

    async def get_variables(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubGetVariablesResponse:
        """
        Retrieve all variables associated with a specified hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/variables",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubGetVariablesResponse,
        )

    async def invite_multiple_users(
        self,
        hub_id: str,
        *,
        emails: List[str] | NotGiven = NOT_GIVEN,
        project_role: Literal["member", "admin", "owner"] | NotGiven = NOT_GIVEN,
        tags: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubInviteMultipleUsersResponse:
        """Invite multiple users to join a hub, by email.

        If users already exist, they are
        added directly, otherwise, an invite is sent. Requires owner or admin
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
            f"/v1/hub/{hub_id}/invite-multiple",
            body=await async_maybe_transform(
                {
                    "emails": emails,
                    "project_role": project_role,
                    "tags": tags,
                },
                hub_invite_multiple_users_params.HubInviteMultipleUsersParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubInviteMultipleUsersResponse,
        )

    async def permanently_delete(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubPermanentlyDeleteResponse:
        """
        Permanently delete a specific hub identified by its UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._delete(
            f"/v1/hub/{hub_id}/permanent",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubPermanentlyDeleteResponse,
        )

    async def remove_user(
        self,
        firebase_id: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubRemoveUserResponse:
        """
        Remove a user from a specific hub, identified by the hub's UUID and user's
        Firebase ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not firebase_id:
            raise ValueError(f"Expected a non-empty value for `firebase_id` but received {firebase_id!r}")
        return await self._delete(
            f"/v1/hub/{hub_id}/remove-user/{firebase_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubRemoveUserResponse,
        )

    async def request_contributor_access(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Request contributor access to a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/request-contributor-access",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def restore(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubRestoreResponse:
        """
        Restore a specific hub, identified by its UUID, that has been previously deleted

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._put(
            f"/v1/hub/{hub_id}/restore",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubRestoreResponse,
        )

    async def search_resources(
        self,
        hub_id: str,
        *,
        search: str,
        process_public_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubSearchResourcesResponse:
        """
        Perform a search operation within a specific hub, identified by its UUID

        Args:
          search: Search query string

          process_public_id: Optional UUID of a document to restrict the search within a specific document

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        return await self._get(
            f"/v1/hub/{hub_id}/search-resources",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "search": search,
                        "process_public_id": process_public_id,
                    },
                    hub_search_resources_params.HubSearchResourcesParams,
                ),
            ),
            cast_to=HubSearchResourcesResponse,
        )

    async def set_column_coloring(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Set column coloring for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/set-column-coloring",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def set_column_format(
        self,
        kind: str,
        *,
        hub_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Set column date formatting for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not kind:
            raise ValueError(f"Expected a non-empty value for `kind` but received {kind!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/set-column-format/{kind}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def train_knowledge_base(
        self,
        hub_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Train the knowledge base for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/train-knowledge-base",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update_heading_styling(
        self,
        style_id: str,
        *,
        hub_id: str,
        bold: bool | NotGiven = NOT_GIVEN,
        colour: str | NotGiven = NOT_GIVEN,
        context: BaseRequestContextParam | NotGiven = NOT_GIVEN,
        font_size: float | NotGiven = NOT_GIVEN,
        italic: bool | NotGiven = NOT_GIVEN,
        numbering_style: int | NotGiven = NOT_GIVEN,
        start_at0: bool | NotGiven = NOT_GIVEN,
        underline: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubUpdateHeadingStylingResponse:
        """
        Update heading styling for a specific hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        if not style_id:
            raise ValueError(f"Expected a non-empty value for `style_id` but received {style_id!r}")
        return await self._post(
            f"/v1/hub/{hub_id}/style/{style_id}",
            body=await async_maybe_transform(
                {
                    "bold": bold,
                    "colour": colour,
                    "context": context,
                    "font_size": font_size,
                    "italic": italic,
                    "numbering_style": numbering_style,
                    "start_at0": start_at0,
                    "underline": underline,
                },
                hub_update_heading_styling_params.HubUpdateHeadingStylingParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubUpdateHeadingStylingResponse,
        )

    async def upload_template(
        self,
        hub_id: str,
        *,
        file: FileTypes | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HubUploadTemplateResponse:
        """
        Upload a template document for a hub

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not hub_id:
            raise ValueError(f"Expected a non-empty value for `hub_id` but received {hub_id!r}")
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/v1/hub/{hub_id}/upload-template",
            body=await async_maybe_transform(body, hub_upload_template_params.HubUploadTemplateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HubUploadTemplateResponse,
        )


class HubResourceWithRawResponse:
    def __init__(self, hub: HubResource) -> None:
        self._hub = hub

        self.create = to_raw_response_wrapper(
            hub.create,
        )
        self.retrieve = to_raw_response_wrapper(
            hub.retrieve,
        )
        self.update = to_raw_response_wrapper(
            hub.update,
        )
        self.delete = to_raw_response_wrapper(
            hub.delete,
        )
        self.ai_search = to_raw_response_wrapper(
            hub.ai_search,
        )
        self.change_user_role = to_raw_response_wrapper(
            hub.change_user_role,
        )
        self.create_heading_styling = to_raw_response_wrapper(
            hub.create_heading_styling,
        )
        self.create_knowledge_base = to_raw_response_wrapper(
            hub.create_knowledge_base,
        )
        self.delete_top_heading_styling = to_raw_response_wrapper(
            hub.delete_top_heading_styling,
        )
        self.duplicate = to_raw_response_wrapper(
            hub.duplicate,
        )
        self.get_ai_answers = to_raw_response_wrapper(
            hub.get_ai_answers,
        )
        self.get_deleted_documents = to_raw_response_wrapper(
            hub.get_deleted_documents,
        )
        self.get_deleted_tables = to_raw_response_wrapper(
            hub.get_deleted_tables,
        )
        self.get_documents = to_raw_response_wrapper(
            hub.get_documents,
        )
        self.get_duplicated_children = to_raw_response_wrapper(
            hub.get_duplicated_children,
        )
        self.get_invited_members = to_raw_response_wrapper(
            hub.get_invited_members,
        )
        self.get_members = to_raw_response_wrapper(
            hub.get_members,
        )
        self.get_notifications = to_raw_response_wrapper(
            hub.get_notifications,
        )
        self.get_resources = to_raw_response_wrapper(
            hub.get_resources,
        )
        self.get_sent_notifications = to_raw_response_wrapper(
            hub.get_sent_notifications,
        )
        self.get_tables = to_raw_response_wrapper(
            hub.get_tables,
        )
        self.get_tags = to_raw_response_wrapper(
            hub.get_tags,
        )
        self.get_variables = to_raw_response_wrapper(
            hub.get_variables,
        )
        self.invite_multiple_users = to_raw_response_wrapper(
            hub.invite_multiple_users,
        )
        self.permanently_delete = to_raw_response_wrapper(
            hub.permanently_delete,
        )
        self.remove_user = to_raw_response_wrapper(
            hub.remove_user,
        )
        self.request_contributor_access = to_raw_response_wrapper(
            hub.request_contributor_access,
        )
        self.restore = to_raw_response_wrapper(
            hub.restore,
        )
        self.search_resources = to_raw_response_wrapper(
            hub.search_resources,
        )
        self.set_column_coloring = to_raw_response_wrapper(
            hub.set_column_coloring,
        )
        self.set_column_format = to_raw_response_wrapper(
            hub.set_column_format,
        )
        self.train_knowledge_base = to_raw_response_wrapper(
            hub.train_knowledge_base,
        )
        self.update_heading_styling = to_raw_response_wrapper(
            hub.update_heading_styling,
        )
        self.upload_template = to_raw_response_wrapper(
            hub.upload_template,
        )

    @cached_property
    def ai_answer(self) -> AIAnswerResourceWithRawResponse:
        return AIAnswerResourceWithRawResponse(self._hub.ai_answer)

    @cached_property
    def invite(self) -> InviteResourceWithRawResponse:
        return InviteResourceWithRawResponse(self._hub.invite)

    @cached_property
    def secrets(self) -> SecretsResourceWithRawResponse:
        return SecretsResourceWithRawResponse(self._hub.secrets)


class AsyncHubResourceWithRawResponse:
    def __init__(self, hub: AsyncHubResource) -> None:
        self._hub = hub

        self.create = async_to_raw_response_wrapper(
            hub.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            hub.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            hub.update,
        )
        self.delete = async_to_raw_response_wrapper(
            hub.delete,
        )
        self.ai_search = async_to_raw_response_wrapper(
            hub.ai_search,
        )
        self.change_user_role = async_to_raw_response_wrapper(
            hub.change_user_role,
        )
        self.create_heading_styling = async_to_raw_response_wrapper(
            hub.create_heading_styling,
        )
        self.create_knowledge_base = async_to_raw_response_wrapper(
            hub.create_knowledge_base,
        )
        self.delete_top_heading_styling = async_to_raw_response_wrapper(
            hub.delete_top_heading_styling,
        )
        self.duplicate = async_to_raw_response_wrapper(
            hub.duplicate,
        )
        self.get_ai_answers = async_to_raw_response_wrapper(
            hub.get_ai_answers,
        )
        self.get_deleted_documents = async_to_raw_response_wrapper(
            hub.get_deleted_documents,
        )
        self.get_deleted_tables = async_to_raw_response_wrapper(
            hub.get_deleted_tables,
        )
        self.get_documents = async_to_raw_response_wrapper(
            hub.get_documents,
        )
        self.get_duplicated_children = async_to_raw_response_wrapper(
            hub.get_duplicated_children,
        )
        self.get_invited_members = async_to_raw_response_wrapper(
            hub.get_invited_members,
        )
        self.get_members = async_to_raw_response_wrapper(
            hub.get_members,
        )
        self.get_notifications = async_to_raw_response_wrapper(
            hub.get_notifications,
        )
        self.get_resources = async_to_raw_response_wrapper(
            hub.get_resources,
        )
        self.get_sent_notifications = async_to_raw_response_wrapper(
            hub.get_sent_notifications,
        )
        self.get_tables = async_to_raw_response_wrapper(
            hub.get_tables,
        )
        self.get_tags = async_to_raw_response_wrapper(
            hub.get_tags,
        )
        self.get_variables = async_to_raw_response_wrapper(
            hub.get_variables,
        )
        self.invite_multiple_users = async_to_raw_response_wrapper(
            hub.invite_multiple_users,
        )
        self.permanently_delete = async_to_raw_response_wrapper(
            hub.permanently_delete,
        )
        self.remove_user = async_to_raw_response_wrapper(
            hub.remove_user,
        )
        self.request_contributor_access = async_to_raw_response_wrapper(
            hub.request_contributor_access,
        )
        self.restore = async_to_raw_response_wrapper(
            hub.restore,
        )
        self.search_resources = async_to_raw_response_wrapper(
            hub.search_resources,
        )
        self.set_column_coloring = async_to_raw_response_wrapper(
            hub.set_column_coloring,
        )
        self.set_column_format = async_to_raw_response_wrapper(
            hub.set_column_format,
        )
        self.train_knowledge_base = async_to_raw_response_wrapper(
            hub.train_knowledge_base,
        )
        self.update_heading_styling = async_to_raw_response_wrapper(
            hub.update_heading_styling,
        )
        self.upload_template = async_to_raw_response_wrapper(
            hub.upload_template,
        )

    @cached_property
    def ai_answer(self) -> AsyncAIAnswerResourceWithRawResponse:
        return AsyncAIAnswerResourceWithRawResponse(self._hub.ai_answer)

    @cached_property
    def invite(self) -> AsyncInviteResourceWithRawResponse:
        return AsyncInviteResourceWithRawResponse(self._hub.invite)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithRawResponse:
        return AsyncSecretsResourceWithRawResponse(self._hub.secrets)


class HubResourceWithStreamingResponse:
    def __init__(self, hub: HubResource) -> None:
        self._hub = hub

        self.create = to_streamed_response_wrapper(
            hub.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            hub.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            hub.update,
        )
        self.delete = to_streamed_response_wrapper(
            hub.delete,
        )
        self.ai_search = to_streamed_response_wrapper(
            hub.ai_search,
        )
        self.change_user_role = to_streamed_response_wrapper(
            hub.change_user_role,
        )
        self.create_heading_styling = to_streamed_response_wrapper(
            hub.create_heading_styling,
        )
        self.create_knowledge_base = to_streamed_response_wrapper(
            hub.create_knowledge_base,
        )
        self.delete_top_heading_styling = to_streamed_response_wrapper(
            hub.delete_top_heading_styling,
        )
        self.duplicate = to_streamed_response_wrapper(
            hub.duplicate,
        )
        self.get_ai_answers = to_streamed_response_wrapper(
            hub.get_ai_answers,
        )
        self.get_deleted_documents = to_streamed_response_wrapper(
            hub.get_deleted_documents,
        )
        self.get_deleted_tables = to_streamed_response_wrapper(
            hub.get_deleted_tables,
        )
        self.get_documents = to_streamed_response_wrapper(
            hub.get_documents,
        )
        self.get_duplicated_children = to_streamed_response_wrapper(
            hub.get_duplicated_children,
        )
        self.get_invited_members = to_streamed_response_wrapper(
            hub.get_invited_members,
        )
        self.get_members = to_streamed_response_wrapper(
            hub.get_members,
        )
        self.get_notifications = to_streamed_response_wrapper(
            hub.get_notifications,
        )
        self.get_resources = to_streamed_response_wrapper(
            hub.get_resources,
        )
        self.get_sent_notifications = to_streamed_response_wrapper(
            hub.get_sent_notifications,
        )
        self.get_tables = to_streamed_response_wrapper(
            hub.get_tables,
        )
        self.get_tags = to_streamed_response_wrapper(
            hub.get_tags,
        )
        self.get_variables = to_streamed_response_wrapper(
            hub.get_variables,
        )
        self.invite_multiple_users = to_streamed_response_wrapper(
            hub.invite_multiple_users,
        )
        self.permanently_delete = to_streamed_response_wrapper(
            hub.permanently_delete,
        )
        self.remove_user = to_streamed_response_wrapper(
            hub.remove_user,
        )
        self.request_contributor_access = to_streamed_response_wrapper(
            hub.request_contributor_access,
        )
        self.restore = to_streamed_response_wrapper(
            hub.restore,
        )
        self.search_resources = to_streamed_response_wrapper(
            hub.search_resources,
        )
        self.set_column_coloring = to_streamed_response_wrapper(
            hub.set_column_coloring,
        )
        self.set_column_format = to_streamed_response_wrapper(
            hub.set_column_format,
        )
        self.train_knowledge_base = to_streamed_response_wrapper(
            hub.train_knowledge_base,
        )
        self.update_heading_styling = to_streamed_response_wrapper(
            hub.update_heading_styling,
        )
        self.upload_template = to_streamed_response_wrapper(
            hub.upload_template,
        )

    @cached_property
    def ai_answer(self) -> AIAnswerResourceWithStreamingResponse:
        return AIAnswerResourceWithStreamingResponse(self._hub.ai_answer)

    @cached_property
    def invite(self) -> InviteResourceWithStreamingResponse:
        return InviteResourceWithStreamingResponse(self._hub.invite)

    @cached_property
    def secrets(self) -> SecretsResourceWithStreamingResponse:
        return SecretsResourceWithStreamingResponse(self._hub.secrets)


class AsyncHubResourceWithStreamingResponse:
    def __init__(self, hub: AsyncHubResource) -> None:
        self._hub = hub

        self.create = async_to_streamed_response_wrapper(
            hub.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            hub.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            hub.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            hub.delete,
        )
        self.ai_search = async_to_streamed_response_wrapper(
            hub.ai_search,
        )
        self.change_user_role = async_to_streamed_response_wrapper(
            hub.change_user_role,
        )
        self.create_heading_styling = async_to_streamed_response_wrapper(
            hub.create_heading_styling,
        )
        self.create_knowledge_base = async_to_streamed_response_wrapper(
            hub.create_knowledge_base,
        )
        self.delete_top_heading_styling = async_to_streamed_response_wrapper(
            hub.delete_top_heading_styling,
        )
        self.duplicate = async_to_streamed_response_wrapper(
            hub.duplicate,
        )
        self.get_ai_answers = async_to_streamed_response_wrapper(
            hub.get_ai_answers,
        )
        self.get_deleted_documents = async_to_streamed_response_wrapper(
            hub.get_deleted_documents,
        )
        self.get_deleted_tables = async_to_streamed_response_wrapper(
            hub.get_deleted_tables,
        )
        self.get_documents = async_to_streamed_response_wrapper(
            hub.get_documents,
        )
        self.get_duplicated_children = async_to_streamed_response_wrapper(
            hub.get_duplicated_children,
        )
        self.get_invited_members = async_to_streamed_response_wrapper(
            hub.get_invited_members,
        )
        self.get_members = async_to_streamed_response_wrapper(
            hub.get_members,
        )
        self.get_notifications = async_to_streamed_response_wrapper(
            hub.get_notifications,
        )
        self.get_resources = async_to_streamed_response_wrapper(
            hub.get_resources,
        )
        self.get_sent_notifications = async_to_streamed_response_wrapper(
            hub.get_sent_notifications,
        )
        self.get_tables = async_to_streamed_response_wrapper(
            hub.get_tables,
        )
        self.get_tags = async_to_streamed_response_wrapper(
            hub.get_tags,
        )
        self.get_variables = async_to_streamed_response_wrapper(
            hub.get_variables,
        )
        self.invite_multiple_users = async_to_streamed_response_wrapper(
            hub.invite_multiple_users,
        )
        self.permanently_delete = async_to_streamed_response_wrapper(
            hub.permanently_delete,
        )
        self.remove_user = async_to_streamed_response_wrapper(
            hub.remove_user,
        )
        self.request_contributor_access = async_to_streamed_response_wrapper(
            hub.request_contributor_access,
        )
        self.restore = async_to_streamed_response_wrapper(
            hub.restore,
        )
        self.search_resources = async_to_streamed_response_wrapper(
            hub.search_resources,
        )
        self.set_column_coloring = async_to_streamed_response_wrapper(
            hub.set_column_coloring,
        )
        self.set_column_format = async_to_streamed_response_wrapper(
            hub.set_column_format,
        )
        self.train_knowledge_base = async_to_streamed_response_wrapper(
            hub.train_knowledge_base,
        )
        self.update_heading_styling = async_to_streamed_response_wrapper(
            hub.update_heading_styling,
        )
        self.upload_template = async_to_streamed_response_wrapper(
            hub.upload_template,
        )

    @cached_property
    def ai_answer(self) -> AsyncAIAnswerResourceWithStreamingResponse:
        return AsyncAIAnswerResourceWithStreamingResponse(self._hub.ai_answer)

    @cached_property
    def invite(self) -> AsyncInviteResourceWithStreamingResponse:
        return AsyncInviteResourceWithStreamingResponse(self._hub.invite)

    @cached_property
    def secrets(self) -> AsyncSecretsResourceWithStreamingResponse:
        return AsyncSecretsResourceWithStreamingResponse(self._hub.secrets)
