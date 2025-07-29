# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "TransformAutoschemaResponse",
    "Data",
    "DataAPIRequest",
    "DataOperation",
    "DataOperationAPIRequest",
    "DataOperationOption",
    "DataOption",
    "Metadata",
]


class DataAPIRequest(BaseModel):
    method: Literal["GET", "POST"]
    """An enumeration."""

    url: str
    """URL endpoint for the API request."""

    body: Optional[object] = None
    """JSON body to send with the API request (for POST)."""

    headers: Optional[object] = None
    """Headers to include with the API request."""


class DataOperationAPIRequest(BaseModel):
    method: Literal["GET", "POST"]
    """An enumeration."""

    url: str
    """URL endpoint for the API request."""

    body: Optional[object] = None
    """JSON body to send with the API request (for POST)."""

    headers: Optional[object] = None
    """Headers to include with the API request."""


class DataOperationOption(BaseModel):
    color: Literal["red", "blue", "orange", "yellow", "green", "gray"]

    name: str

    visual_index: int

    linked_entity_id: Optional[str] = None
    """The ID of the entity this option belongs to.

    This is used for entity field options.
    """


class DataOperation(BaseModel):
    column_name: str
    """Name of the column to be transformed.

    Any alphanumeric characters are allowed. Must be unique.
    """

    column_type: Literal[
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
    """An enumeration."""

    task_description: str
    """Description of the task to be performed.

    If `transform_type` is not one of [`parse`, `manual`], the task description must
    contain a reference to another column. Otherwise, the task description may be
    left blank.
    """

    transform_type: Literal[
        "extraction", "classification", "generation", "manual", "api_request", "parse", "run_function"
    ]
    """An enumeration."""

    api_request: Optional[DataOperationAPIRequest] = None
    """
    For transform_type='api_request', specify the HTTP method, URL, header, and
    body.
    """

    default_value: Optional[object] = None
    """
    The default value to use if has_default is true and no value is found in the
    document. The value you should return is stored under the 'value' key.
    """

    has_default: Optional[bool] = None
    """If true, use the default value specified in default_value.

    If false, return null if no value found.
    """

    operations: Optional[List[object]] = None
    """Required when column_type is `object` or `list`.

    Defines the structure of object or list operations. If column_type is `list`,
    then operations should only be of length 1 since `list` can only be of one type.
    If column_type is `object`, then operations can be longer of length one (and
    optionally be nested.)
    """

    options: Optional[List[DataOperationOption]] = None
    """Options for select fields."""

    output_values: Optional[Dict[str, str]] = None
    """NOTE: only valid with classification tasks.

    Output values of the transformation operation.
    """

    prompt_type: Optional[Literal["text", "multimodal"]] = None
    """An enumeration."""

    run_function_code: Optional[str] = None
    """For transform_type='run_function', the javascript code to run on AWS lambda"""


class DataOption(BaseModel):
    color: Literal["red", "blue", "orange", "yellow", "green", "gray"]

    name: str

    visual_index: int

    linked_entity_id: Optional[str] = None
    """The ID of the entity this option belongs to.

    This is used for entity field options.
    """


class Data(BaseModel):
    column_name: str
    """Name of the column to be transformed.

    Any alphanumeric characters are allowed. Must be unique.
    """

    column_type: Literal[
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
    """An enumeration."""

    task_description: str
    """Description of the task to be performed.

    If `transform_type` is not one of [`parse`, `manual`], the task description must
    contain a reference to another column. Otherwise, the task description may be
    left blank.
    """

    transform_type: Literal[
        "extraction", "classification", "generation", "manual", "api_request", "parse", "run_function"
    ]
    """An enumeration."""

    id: Optional[str] = None

    api_request: Optional[DataAPIRequest] = None
    """
    For transform_type='api_request', specify the HTTP method, URL, header, and
    body.
    """

    default_value: Optional[object] = None
    """
    The default value to use if has_default is true and no value is found in the
    document. The value you should return is stored under the 'value' key.
    """

    has_default: Optional[bool] = None
    """If true, use the default value specified in default_value.

    If false, return null if no value found.
    """

    operations: Optional[List[DataOperation]] = None
    """Required when column_type is `object` or `list`.

    Defines the structure of object or list operations. If column_type is `list`,
    then operations should only be of length 1 since `list` can only be of one type.
    If column_type is `object`, then operations can be longer of length one (and
    optionally be nested.)
    """

    options: Optional[List[DataOption]] = None
    """Options for select fields."""

    output_values: Optional[Dict[str, str]] = None
    """NOTE: only valid with classification tasks.

    Output values of the transformation operation.
    """

    prompt_type: Optional[Literal["text", "multimodal"]] = None
    """An enumeration."""

    run_function_code: Optional[str] = None
    """For transform_type='run_function', the javascript code to run on AWS lambda"""


class Metadata(BaseModel):
    total_generated: int


class TransformAutoschemaResponse(BaseModel):
    data: List[Data]

    message: str

    metadata: Metadata
