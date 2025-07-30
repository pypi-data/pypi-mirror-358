# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

from ..types import asset_list_params, asset_upload_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.assets import Assets
from ..types.asset_delete_response import AssetDeleteResponse

__all__ = ["AssetsResource", "AsyncAssetsResource"]


class AssetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#with_streaming_response
        """
        return AssetsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        asset_ids: List[str] | NotGiven = NOT_GIVEN,
        entity_field_id: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        operation_id: str | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["updated_at", "created_at", "id"] | NotGiven = NOT_GIVEN,
        proj_id: str | NotGiven = NOT_GIVEN,
        row_id: str | NotGiven = NOT_GIVEN,
        status: Literal["uploading", "uploaded", "failed_upload", "processing", "not_processed", "processed"]
        | NotGiven = NOT_GIVEN,
        transform_id: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Assets:
        """
        Retrieve asset IDs from a project.

        Parameters:

        - asset_ids (List[str], optional): The list of asset IDs to retrieve. This is
          optional, but will override the proj_id if provided.
        - proj_id (str, optional): The id of the project. This is optional, but will be
          used if asset_ids is not provided.
        - status (AssetStatus, optional): Filters the results based on the status of the
          assets.
        - limit (int, optional): The number of transformations to retrieve.
        - offset (int, optional): The offset to start retrieving transformations from.
        - order_by (str, optional): The column to order the transformations by.
        - order (str, optional): The order to sort the transformations by.

        If neither asset_ids or proj_id is provided, all assets will be retrieved.

        Returns:

        - dict: A dict containing the all the asset data.

        Args:
          asset_ids: List of asset IDs to retrieve.

          entity_field_id: Entity field ID where the asset belongs

          entity_id: Entity ID where the asset belongs

          operation_id: Operation ID where the asset belongs

          order: An enumeration.

          order_by: An enumeration.

          proj_id: The id of the project.

          row_id: Row ID where the asset belongs

          status: An enumeration.

          transform_id: The id of the transformation.

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
        return self._get(
            "/v1/assets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "asset_ids": asset_ids,
                        "entity_field_id": entity_field_id,
                        "entity_id": entity_id,
                        "limit": limit,
                        "offset": offset,
                        "operation_id": operation_id,
                        "order": order,
                        "order_by": order_by,
                        "proj_id": proj_id,
                        "row_id": row_id,
                        "status": status,
                        "transform_id": transform_id,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            cast_to=Assets,
        )

    def delete(
        self,
        asset_id: str,
        *,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetDeleteResponse:
        """
        Delete an asset from the project.

        Parameters:

        - asset_id (str): The asset ID to delete. Returns:
        - bool: A boolean indicating if the asset was deleted successfully.

        Args:
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
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return self._delete(
            f"/v1/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetDeleteResponse,
        )

    def upload(
        self,
        *,
        urls: List[str],
        cells: Iterable[asset_upload_params.Cell] | NotGiven = NOT_GIVEN,
        chunk_strategy: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        ext_file_names: List[str] | NotGiven = NOT_GIVEN,
        ext_ids: List[str] | NotGiven = NOT_GIVEN,
        file_type: str | NotGiven = NOT_GIVEN,
        file_types: List[str] | NotGiven = NOT_GIVEN,
        include_header: bool | NotGiven = NOT_GIVEN,
        main_keys: List[str] | NotGiven = NOT_GIVEN,
        parse_strategy: str | NotGiven = NOT_GIVEN,
        process_with_workflow: bool | NotGiven = NOT_GIVEN,
        proj_id: str | NotGiven = NOT_GIVEN,
        transform_id: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Assets:
        """
        Upload Assets

        Args:
          urls: A list of file URLs to be downloaded and processed during the upload.

          cells: Optional. If provided, must also provide transform_id. Additionally, every url
              required a cell to upload the file into.

          chunk_strategy: Optional. Define how files should be split during processing. Supported values
              are `new_line` (split rows by newline for CSV/Excel) or `None` (no splitting).

          entity_id: The ID of the entity to which the assets will be uploaded and assigned.

          ext_file_names: Optional. Names for the files to be uploaded. If not provided, names will be
              derived from the URLs.

          ext_ids: Optional. External identifiers for the files, useful for mapping or reference.

          file_type: Default file type to apply to all files if individual types are not specified.

          file_types: Optional. Specify the file types for each URL (e.g., 'csv', 'xlsx'). If not
              provided, defaults will be used based on content.

          include_header: Specify whether the input files include a header row. This applies to CSV or
              Excel files only.

          main_keys: Optional. Column names to be used as unique identifiers when chunking data. If
              not provided, all columns will be combined to generate unique identifiers.

          parse_strategy: Optional. Strategy to be used for parsing files during processing.

          process_with_workflow: Optional. If true, the assets will be processed with the workflow configured on
              your project.

          proj_id: The ID of the project to which the assets will be uploaded and assigned.

          transform_id: Specify if the uploaded assets should be processed exclusively by a particular
              transformation.

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
            "/v1/assets/upload",
            body=maybe_transform(
                {
                    "urls": urls,
                    "cells": cells,
                    "chunk_strategy": chunk_strategy,
                    "entity_id": entity_id,
                    "ext_file_names": ext_file_names,
                    "ext_ids": ext_ids,
                    "file_type": file_type,
                    "file_types": file_types,
                    "include_header": include_header,
                    "main_keys": main_keys,
                    "parse_strategy": parse_strategy,
                    "process_with_workflow": process_with_workflow,
                    "proj_id": proj_id,
                    "transform_id": transform_id,
                },
                asset_upload_params.AssetUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Assets,
        )


class AsyncAssetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Trellis-insights/trellis-python-sdk#with_streaming_response
        """
        return AsyncAssetsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        asset_ids: List[str] | NotGiven = NOT_GIVEN,
        entity_field_id: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        operation_id: str | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        order_by: Literal["updated_at", "created_at", "id"] | NotGiven = NOT_GIVEN,
        proj_id: str | NotGiven = NOT_GIVEN,
        row_id: str | NotGiven = NOT_GIVEN,
        status: Literal["uploading", "uploaded", "failed_upload", "processing", "not_processed", "processed"]
        | NotGiven = NOT_GIVEN,
        transform_id: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Assets:
        """
        Retrieve asset IDs from a project.

        Parameters:

        - asset_ids (List[str], optional): The list of asset IDs to retrieve. This is
          optional, but will override the proj_id if provided.
        - proj_id (str, optional): The id of the project. This is optional, but will be
          used if asset_ids is not provided.
        - status (AssetStatus, optional): Filters the results based on the status of the
          assets.
        - limit (int, optional): The number of transformations to retrieve.
        - offset (int, optional): The offset to start retrieving transformations from.
        - order_by (str, optional): The column to order the transformations by.
        - order (str, optional): The order to sort the transformations by.

        If neither asset_ids or proj_id is provided, all assets will be retrieved.

        Returns:

        - dict: A dict containing the all the asset data.

        Args:
          asset_ids: List of asset IDs to retrieve.

          entity_field_id: Entity field ID where the asset belongs

          entity_id: Entity ID where the asset belongs

          operation_id: Operation ID where the asset belongs

          order: An enumeration.

          order_by: An enumeration.

          proj_id: The id of the project.

          row_id: Row ID where the asset belongs

          status: An enumeration.

          transform_id: The id of the transformation.

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
        return await self._get(
            "/v1/assets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "asset_ids": asset_ids,
                        "entity_field_id": entity_field_id,
                        "entity_id": entity_id,
                        "limit": limit,
                        "offset": offset,
                        "operation_id": operation_id,
                        "order": order,
                        "order_by": order_by,
                        "proj_id": proj_id,
                        "row_id": row_id,
                        "status": status,
                        "transform_id": transform_id,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            cast_to=Assets,
        )

    async def delete(
        self,
        asset_id: str,
        *,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetDeleteResponse:
        """
        Delete an asset from the project.

        Parameters:

        - asset_id (str): The asset ID to delete. Returns:
        - bool: A boolean indicating if the asset was deleted successfully.

        Args:
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
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {**strip_not_given({"API-Version": api_version}), **(extra_headers or {})}
        return await self._delete(
            f"/v1/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetDeleteResponse,
        )

    async def upload(
        self,
        *,
        urls: List[str],
        cells: Iterable[asset_upload_params.Cell] | NotGiven = NOT_GIVEN,
        chunk_strategy: str | NotGiven = NOT_GIVEN,
        entity_id: str | NotGiven = NOT_GIVEN,
        ext_file_names: List[str] | NotGiven = NOT_GIVEN,
        ext_ids: List[str] | NotGiven = NOT_GIVEN,
        file_type: str | NotGiven = NOT_GIVEN,
        file_types: List[str] | NotGiven = NOT_GIVEN,
        include_header: bool | NotGiven = NOT_GIVEN,
        main_keys: List[str] | NotGiven = NOT_GIVEN,
        parse_strategy: str | NotGiven = NOT_GIVEN,
        process_with_workflow: bool | NotGiven = NOT_GIVEN,
        proj_id: str | NotGiven = NOT_GIVEN,
        transform_id: str | NotGiven = NOT_GIVEN,
        api_version: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Assets:
        """
        Upload Assets

        Args:
          urls: A list of file URLs to be downloaded and processed during the upload.

          cells: Optional. If provided, must also provide transform_id. Additionally, every url
              required a cell to upload the file into.

          chunk_strategy: Optional. Define how files should be split during processing. Supported values
              are `new_line` (split rows by newline for CSV/Excel) or `None` (no splitting).

          entity_id: The ID of the entity to which the assets will be uploaded and assigned.

          ext_file_names: Optional. Names for the files to be uploaded. If not provided, names will be
              derived from the URLs.

          ext_ids: Optional. External identifiers for the files, useful for mapping or reference.

          file_type: Default file type to apply to all files if individual types are not specified.

          file_types: Optional. Specify the file types for each URL (e.g., 'csv', 'xlsx'). If not
              provided, defaults will be used based on content.

          include_header: Specify whether the input files include a header row. This applies to CSV or
              Excel files only.

          main_keys: Optional. Column names to be used as unique identifiers when chunking data. If
              not provided, all columns will be combined to generate unique identifiers.

          parse_strategy: Optional. Strategy to be used for parsing files during processing.

          process_with_workflow: Optional. If true, the assets will be processed with the workflow configured on
              your project.

          proj_id: The ID of the project to which the assets will be uploaded and assigned.

          transform_id: Specify if the uploaded assets should be processed exclusively by a particular
              transformation.

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
            "/v1/assets/upload",
            body=await async_maybe_transform(
                {
                    "urls": urls,
                    "cells": cells,
                    "chunk_strategy": chunk_strategy,
                    "entity_id": entity_id,
                    "ext_file_names": ext_file_names,
                    "ext_ids": ext_ids,
                    "file_type": file_type,
                    "file_types": file_types,
                    "include_header": include_header,
                    "main_keys": main_keys,
                    "parse_strategy": parse_strategy,
                    "process_with_workflow": process_with_workflow,
                    "proj_id": proj_id,
                    "transform_id": transform_id,
                },
                asset_upload_params.AssetUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Assets,
        )


class AssetsResourceWithRawResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_raw_response_wrapper(
            assets.list,
        )
        self.delete = to_raw_response_wrapper(
            assets.delete,
        )
        self.upload = to_raw_response_wrapper(
            assets.upload,
        )


class AsyncAssetsResourceWithRawResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_raw_response_wrapper(
            assets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            assets.delete,
        )
        self.upload = async_to_raw_response_wrapper(
            assets.upload,
        )


class AssetsResourceWithStreamingResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_streamed_response_wrapper(
            assets.list,
        )
        self.delete = to_streamed_response_wrapper(
            assets.delete,
        )
        self.upload = to_streamed_response_wrapper(
            assets.upload,
        )


class AsyncAssetsResourceWithStreamingResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_streamed_response_wrapper(
            assets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            assets.delete,
        )
        self.upload = async_to_streamed_response_wrapper(
            assets.upload,
        )
