# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, cast
from typing_extensions import Literal

import httpx

from ...types import transform_list_params, transform_create_params, transform_update_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.transform_list_response import TransformListResponse
from ...types.transform_create_response import TransformCreateResponse
from ...types.transform_update_response import TransformUpdateResponse
from ...types.transform_autoschema_response import TransformAutoschemaResponse

__all__ = ["TransformsResource", "AsyncTransformsResource"]


class TransformsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TransformsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#accessing-raw-response-data-eg-headers
        """
        return TransformsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TransformsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#with_streaming_response
        """
        return TransformsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        proj_id: str,
        transform_params: transform_create_params.TransformParams,
        actions: transform_create_params.Actions | NotGiven = NOT_GIVEN,
        transform_name: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformCreateResponse:
        """
        Run the transformation defined in transformation params for all the assets in
        the project

        Args: transform_id (str): The ID of the transformation to run.

        Returns: {"message": "Transformation initiated", "transform_id": transform_id}

        Args:
          proj_id: The id of the project.

          actions: Enable actions specific to this transformation.

          transform_name: The transform_name parameter is an optional parameter that provides a
              human-readable name or description for the transformation, which can be useful
              for identifying and referencing transformations. If provided, the transform_name
              parameter should be a string. If not provided, the value of transform_name will
              be None.

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._post(
            "/v1/transforms/create",
            body=maybe_transform(
                {
                    "proj_id": proj_id,
                    "transform_params": transform_params,
                    "actions": actions,
                    "transform_name": transform_name,
                },
                transform_create_params.TransformCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransformCreateResponse,
        )

    def update(
        self,
        transform_id: str,
        *,
        asset_ids: List[str] | NotGiven = NOT_GIVEN,
        include_reference: bool | NotGiven = NOT_GIVEN,
        row_ids: List[str] | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformUpdateResponse:
        """
        Refreshes an existing transform by re-running operations on rows that need
        updating.

        Args:
          asset_ids: List of asset ids to refresh. Don't provide if providing row_ids

          row_ids: List of row ids to refresh. Don't provide if providing asset_ids

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transform_id:
            raise ValueError(f"Expected a non-empty value for `transform_id` but received {transform_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._patch(
            f"/v1/transforms/{transform_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "asset_ids": asset_ids,
                        "include_reference": include_reference,
                        "row_ids": row_ids,
                    },
                    transform_update_params.TransformUpdateParams,
                ),
            ),
            cast_to=TransformUpdateResponse,
        )

    def list(
        self,
        *,
        include_transform_params: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["updated_at", "created_at", "id"] | NotGiven = NOT_GIVEN,
        proj_ids: List[str] | NotGiven = NOT_GIVEN,
        search_term: str | NotGiven = NOT_GIVEN,
        transform_ids: List[str] | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformListResponse:
        """
        Retrieve all transformation associated with you.

        Parameters:

        - transform_ids (list, optional): The IDs of the transformations to retrieve.
        - proj_ids (list, optional): The ids of the projects to retrieve transformations
          from.
        - include_params (bool, optional): Include metadata in the response such as the
          transform_params. Defaults to false.

        Returns:

        - dict: A dict containing all the transformations associated with you.

        Args:
          include_transform_params: Boolean flag to include transform params, which includes the operations.

          order: An enumeration.

          order_by: An enumeration.

          proj_ids: List of project ids to retrieve transformations from.

          search_term: Search term to filter transformations against their id and name.

          transform_ids: List of transform IDs to retrieve.

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return cast(
            TransformListResponse,
            self._get(
                "/v1/transforms",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {
                            "include_transform_params": include_transform_params,
                            "limit": limit,
                            "offset": offset,
                            "order": order,
                            "order_by": order_by,
                            "proj_ids": proj_ids,
                            "search_term": search_term,
                            "transform_ids": transform_ids,
                        },
                        transform_list_params.TransformListParams,
                    ),
                ),
                cast_to=cast(
                    Any, TransformListResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def autoschema(
        self,
        transform_id: str,
        *,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformAutoschemaResponse:
        """
        Get Autoschema

        Args:
          transform_id: The transform_id to get the autoschema for

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transform_id:
            raise ValueError(f"Expected a non-empty value for `transform_id` but received {transform_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._get(
            f"/v1/transforms/{transform_id}/autoschema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransformAutoschemaResponse,
        )


class AsyncTransformsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTransformsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTransformsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTransformsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#with_streaming_response
        """
        return AsyncTransformsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        proj_id: str,
        transform_params: transform_create_params.TransformParams,
        actions: transform_create_params.Actions | NotGiven = NOT_GIVEN,
        transform_name: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformCreateResponse:
        """
        Run the transformation defined in transformation params for all the assets in
        the project

        Args: transform_id (str): The ID of the transformation to run.

        Returns: {"message": "Transformation initiated", "transform_id": transform_id}

        Args:
          proj_id: The id of the project.

          actions: Enable actions specific to this transformation.

          transform_name: The transform_name parameter is an optional parameter that provides a
              human-readable name or description for the transformation, which can be useful
              for identifying and referencing transformations. If provided, the transform_name
              parameter should be a string. If not provided, the value of transform_name will
              be None.

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._post(
            "/v1/transforms/create",
            body=await async_maybe_transform(
                {
                    "proj_id": proj_id,
                    "transform_params": transform_params,
                    "actions": actions,
                    "transform_name": transform_name,
                },
                transform_create_params.TransformCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransformCreateResponse,
        )

    async def update(
        self,
        transform_id: str,
        *,
        asset_ids: List[str] | NotGiven = NOT_GIVEN,
        include_reference: bool | NotGiven = NOT_GIVEN,
        row_ids: List[str] | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformUpdateResponse:
        """
        Refreshes an existing transform by re-running operations on rows that need
        updating.

        Args:
          asset_ids: List of asset ids to refresh. Don't provide if providing row_ids

          row_ids: List of row ids to refresh. Don't provide if providing asset_ids

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transform_id:
            raise ValueError(f"Expected a non-empty value for `transform_id` but received {transform_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._patch(
            f"/v1/transforms/{transform_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "asset_ids": asset_ids,
                        "include_reference": include_reference,
                        "row_ids": row_ids,
                    },
                    transform_update_params.TransformUpdateParams,
                ),
            ),
            cast_to=TransformUpdateResponse,
        )

    async def list(
        self,
        *,
        include_transform_params: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["updated_at", "created_at", "id"] | NotGiven = NOT_GIVEN,
        proj_ids: List[str] | NotGiven = NOT_GIVEN,
        search_term: str | NotGiven = NOT_GIVEN,
        transform_ids: List[str] | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformListResponse:
        """
        Retrieve all transformation associated with you.

        Parameters:

        - transform_ids (list, optional): The IDs of the transformations to retrieve.
        - proj_ids (list, optional): The ids of the projects to retrieve transformations
          from.
        - include_params (bool, optional): Include metadata in the response such as the
          transform_params. Defaults to false.

        Returns:

        - dict: A dict containing all the transformations associated with you.

        Args:
          include_transform_params: Boolean flag to include transform params, which includes the operations.

          order: An enumeration.

          order_by: An enumeration.

          proj_ids: List of project ids to retrieve transformations from.

          search_term: Search term to filter transformations against their id and name.

          transform_ids: List of transform IDs to retrieve.

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return cast(
            TransformListResponse,
            await self._get(
                "/v1/transforms",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {
                            "include_transform_params": include_transform_params,
                            "limit": limit,
                            "offset": offset,
                            "order": order,
                            "order_by": order_by,
                            "proj_ids": proj_ids,
                            "search_term": search_term,
                            "transform_ids": transform_ids,
                        },
                        transform_list_params.TransformListParams,
                    ),
                ),
                cast_to=cast(
                    Any, TransformListResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def autoschema(
        self,
        transform_id: str,
        *,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TransformAutoschemaResponse:
        """
        Get Autoschema

        Args:
          transform_id: The transform_id to get the autoschema for

          api_version: Pass in an API version to guarantee a consistent response format.

              The latest version should be used for all new API calls. Existing API calls
              should be updated to the latest version when possible.

              **Valid versions:**

              - Latest API version (recommended): `2025-03`

              - Previous API version (maintenance mode): `2025-02`

              If no API version header is included, the response format is considered unstable
              and could change without notice (not recommended).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not transform_id:
            raise ValueError(f"Expected a non-empty value for `transform_id` but received {transform_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._get(
            f"/v1/transforms/{transform_id}/autoschema",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransformAutoschemaResponse,
        )


class TransformsResourceWithRawResponse:
    def __init__(self, transforms: TransformsResource) -> None:
        self._transforms = transforms

        self.create = to_raw_response_wrapper(
            transforms.create,
        )
        self.update = to_raw_response_wrapper(
            transforms.update,
        )
        self.list = to_raw_response_wrapper(
            transforms.list,
        )
        self.autoschema = to_raw_response_wrapper(
            transforms.autoschema,
        )


class AsyncTransformsResourceWithRawResponse:
    def __init__(self, transforms: AsyncTransformsResource) -> None:
        self._transforms = transforms

        self.create = async_to_raw_response_wrapper(
            transforms.create,
        )
        self.update = async_to_raw_response_wrapper(
            transforms.update,
        )
        self.list = async_to_raw_response_wrapper(
            transforms.list,
        )
        self.autoschema = async_to_raw_response_wrapper(
            transforms.autoschema,
        )


class TransformsResourceWithStreamingResponse:
    def __init__(self, transforms: TransformsResource) -> None:
        self._transforms = transforms

        self.create = to_streamed_response_wrapper(
            transforms.create,
        )
        self.update = to_streamed_response_wrapper(
            transforms.update,
        )
        self.list = to_streamed_response_wrapper(
            transforms.list,
        )
        self.autoschema = to_streamed_response_wrapper(
            transforms.autoschema,
        )


class AsyncTransformsResourceWithStreamingResponse:
    def __init__(self, transforms: AsyncTransformsResource) -> None:
        self._transforms = transforms

        self.create = async_to_streamed_response_wrapper(
            transforms.create,
        )
        self.update = async_to_streamed_response_wrapper(
            transforms.update,
        )
        self.list = async_to_streamed_response_wrapper(
            transforms.list,
        )
        self.autoschema = async_to_streamed_response_wrapper(
            transforms.autoschema,
        )
