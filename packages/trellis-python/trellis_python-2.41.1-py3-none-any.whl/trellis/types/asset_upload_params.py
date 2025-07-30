# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AssetUploadParams", "Cell"]


class AssetUploadParams(TypedDict, total=False):
    urls: Required[List[str]]
    """A list of file URLs to be downloaded and processed during the upload."""

    cells: Iterable[Cell]
    """Optional.

    If provided, must also provide transform_id. Additionally, every url required a
    cell to upload the file into.
    """

    chunk_strategy: str
    """Optional.

    Define how files should be split during processing. Supported values are
    `new_line` (split rows by newline for CSV/Excel) or `None` (no splitting).
    """

    entity_id: str
    """The ID of the entity to which the assets will be uploaded and assigned."""

    ext_file_names: List[str]
    """Optional.

    Names for the files to be uploaded. If not provided, names will be derived from
    the URLs.
    """

    ext_ids: List[str]
    """Optional. External identifiers for the files, useful for mapping or reference."""

    file_type: str
    """Default file type to apply to all files if individual types are not specified."""

    file_types: List[str]
    """Optional.

    Specify the file types for each URL (e.g., 'csv', 'xlsx'). If not provided,
    defaults will be used based on content.
    """

    include_header: bool
    """Specify whether the input files include a header row.

    This applies to CSV or Excel files only.
    """

    main_keys: List[str]
    """Optional.

    Column names to be used as unique identifiers when chunking data. If not
    provided, all columns will be combined to generate unique identifiers.
    """

    parse_strategy: str
    """Optional. Strategy to be used for parsing files during processing."""

    process_with_workflow: bool
    """Optional.

    If true, the assets will be processed with the workflow configured on your
    project.
    """

    proj_id: str
    """The ID of the project to which the assets will be uploaded and assigned."""

    transform_id: str
    """
    Specify if the uploaded assets should be processed exclusively by a particular
    transformation.
    """

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


class Cell(TypedDict, total=False):
    row_id: Required[str]

    field_id: str

    op_id: str
