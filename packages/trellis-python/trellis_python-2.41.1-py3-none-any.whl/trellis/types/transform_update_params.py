# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TransformUpdateParams"]


class TransformUpdateParams(TypedDict, total=False):
    asset_ids: List[str]
    """List of asset ids to refresh. Don't provide if providing row_ids"""

    include_reference: bool

    row_ids: List[str]
    """List of row ids to refresh. Don't provide if providing asset_ids"""

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
