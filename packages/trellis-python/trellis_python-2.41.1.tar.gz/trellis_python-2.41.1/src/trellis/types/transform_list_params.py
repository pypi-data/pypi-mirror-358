# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformListParams"]


class TransformListParams(TypedDict, total=False):
    include_transform_params: bool
    """Boolean flag to include transform params, which includes the operations."""

    limit: int

    offset: int

    order: Literal["asc", "desc"]
    """An enumeration."""

    order_by: Literal["updated_at", "created_at", "id"]
    """An enumeration."""

    proj_ids: List[str]
    """List of project ids to retrieve transformations from."""

    search_term: str
    """Search term to filter transformations against their id and name."""

    transform_ids: List[str]
    """List of transform IDs to retrieve."""

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
