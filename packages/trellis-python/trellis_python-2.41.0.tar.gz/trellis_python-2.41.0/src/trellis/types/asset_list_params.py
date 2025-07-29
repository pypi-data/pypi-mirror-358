# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AssetListParams"]


class AssetListParams(TypedDict, total=False):
    asset_ids: List[str]
    """List of asset IDs to retrieve."""

    entity_field_id: str
    """Entity field ID where the asset belongs"""

    entity_id: str
    """Entity ID where the asset belongs"""

    limit: int

    offset: int

    operation_id: str
    """Operation ID where the asset belongs"""

    order: Literal["asc", "desc"]
    """An enumeration."""

    order_by: Literal["updated_at", "created_at", "id"]
    """An enumeration."""

    proj_id: str
    """The id of the project."""

    row_id: str
    """Row ID where the asset belongs"""

    status: Literal["uploading", "uploaded", "failed_upload", "processing", "not_processed", "processed"]
    """An enumeration."""

    transform_id: str
    """The id of the transformation."""

    api_version: Annotated[str, PropertyInfo(alias="API-Version")]
    """Pass in an API version to guarantee a consistent response format.

    The latest version should be used for all new API calls. Existing API calls
    should be updated to the latest version when possible.

    **Valid versions:**

    - Latest API version (recommended): `2025-03`

    - Previous API version (maintenance mode): `2025-02`

    If no API version header is included, the response format is considered unstable
    and could change without notice (not recommended).
    """
