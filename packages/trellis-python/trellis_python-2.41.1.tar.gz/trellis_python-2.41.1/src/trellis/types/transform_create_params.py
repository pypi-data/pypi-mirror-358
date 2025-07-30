# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "TransformCreateParams",
    "TransformParams",
    "TransformParamsOperation",
    "TransformParamsOperationAPIRequest",
    "TransformParamsOperationOption",
    "TransformParamsTablePreferences",
    "Actions",
]


class TransformCreateParams(TypedDict, total=False):
    proj_id: Required[str]
    """The id of the project."""

    transform_params: Required[TransformParams]

    actions: Actions
    """Enable actions specific to this transformation."""

    transform_name: str
    """
    The transform_name parameter is an optional parameter that provides a
    human-readable name or description for the transformation, which can be useful
    for identifying and referencing transformations. If provided, the transform_name
    parameter should be a string. If not provided, the value of transform_name will
    be None.
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


class TransformParamsOperationAPIRequest(TypedDict, total=False):
    method: Required[Literal["GET", "POST"]]
    """An enumeration."""

    url: Required[str]
    """URL endpoint for the API request."""

    body: object
    """JSON body to send with the API request (for POST)."""

    headers: object
    """Headers to include with the API request."""


class TransformParamsOperationOption(TypedDict, total=False):
    color: Required[Literal["red", "blue", "orange", "yellow", "green", "gray"]]

    name: Required[str]

    visual_index: Required[int]

    linked_entity_id: str
    """The ID of the entity this option belongs to.

    This is used for entity field options.
    """


class TransformParamsOperation(TypedDict, total=False):
    column_name: Required[str]
    """Name of the column to be transformed.

    Any alphanumeric characters are allowed. Must be unique.
    """

    column_type: Required[
        Literal[
            "text",
            "integer",
            "numeric",
            "boolean",
            "list",
            "object",
            "string",
            "number",
            "time",
            "date",
            "text[]",
            "jsonb",
            "assets",
            "short_text",
            "single_select",
            "multi_select",
            "row_relation",
        ]
    ]
    """An enumeration."""

    task_description: Required[str]
    """Description of the task to be performed.

    If `transform_type` is not one of [`parse`, `manual`], the task description must
    contain a reference to another column. Otherwise, the task description may be
    left blank.
    """

    transform_type: Required[
        Literal["extraction", "classification", "generation", "manual", "api_request", "parse", "run_function"]
    ]
    """An enumeration."""

    api_request: TransformParamsOperationAPIRequest
    """
    For transform_type='api_request', specify the HTTP method, URL, header, and
    body.
    """

    default_value: object
    """
    The default value to use if has_default is true and no value is found in the
    document. The value you should return is stored under the 'value' key.
    """

    has_default: bool
    """If true, use the default value specified in default_value.

    If false, return null if no value found.
    """

    operations: Iterable[object]
    """Required when column_type is `object` or `list`.

    Defines the structure of object or list operations. If column_type is `list`,
    then operations should only be of length 1 since `list` can only be of one type.
    If column_type is `object`, then operations can be longer of length one (and
    optionally be nested.)
    """

    options: Iterable[TransformParamsOperationOption]
    """Options for select fields."""

    output_values: Dict[str, str]
    """NOTE: only valid with classification tasks.

    Output values of the transformation operation.
    """

    prompt_type: Literal["text", "multimodal"]
    """An enumeration."""

    run_function_code: str
    """For transform_type='run_function', the javascript code to run on AWS lambda"""


class TransformParamsTablePreferences(TypedDict, total=False):
    advanced_reasoning: bool
    """Using advanced reasoning when extracting rows from the tables.

    Transformation becomes slower and more computationally intensive
    """

    included_table_names: List[str]
    """Parameter that specifies the table names to be included for table transforms."""


class TransformParams(TypedDict, total=False):
    model: Required[str]
    """The model to be used for the transformation.

    Must be one of 'trellis-scale', 'trellis-premium', or 'trellis-vertix'
    """

    mode: str
    """The mode to be used for the transformation.

    Must be one of 'document' or 'table'
    """

    operations: Iterable[TransformParamsOperation]
    """A list of columns used to extract, classify and generate data from your assets.

    At least one column of `transform_type = 'parse'` and `column_type = 'assets'`
    is required. If your account was created before March 1st, we will automatically
    create an `assets`-type column on transform creation.
    """

    table_preferences: TransformParamsTablePreferences
    """Applicable for table transform mode only.

    Optional parameter that specifies the table names to be included for table
    transforms.
    """


class Actions(TypedDict, total=False):
    run_on_extract: bool
    """Enable immediate transformation runs on asset uploaded and extracted"""
