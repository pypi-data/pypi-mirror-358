# Transforms

Types:

```python
from trellis.types import (
    TransformCreateResponse,
    TransformUpdateResponse,
    TransformListResponse,
    TransformAutoschemaResponse,
)
```

Methods:

- <code title="post /v1/transforms/create">client.transforms.<a href="./src/trellis/resources/transforms/transforms.py">create</a>(\*\*<a href="src/trellis/types/transform_create_params.py">params</a>) -> <a href="./src/trellis/types/transform_create_response.py">TransformCreateResponse</a></code>
- <code title="patch /v1/transforms/{transform_id}">client.transforms.<a href="./src/trellis/resources/transforms/transforms.py">update</a>(transform_id, \*\*<a href="src/trellis/types/transform_update_params.py">params</a>) -> <a href="./src/trellis/types/transform_update_response.py">TransformUpdateResponse</a></code>
- <code title="get /v1/transforms">client.transforms.<a href="./src/trellis/resources/transforms/transforms.py">list</a>(\*\*<a href="src/trellis/types/transform_list_params.py">params</a>) -> <a href="./src/trellis/types/transform_list_response.py">TransformListResponse</a></code>
- <code title="get /v1/transforms/{transform_id}/autoschema">client.transforms.<a href="./src/trellis/resources/transforms/transforms.py">autoschema</a>(transform_id) -> <a href="./src/trellis/types/transform_autoschema_response.py">TransformAutoschemaResponse</a></code>

# Projects

Types:

```python
from trellis.types import ProjectCreateResponse, ProjectListResponse, ProjectDeleteResponse
```

Methods:

- <code title="post /v1/projects/create">client.projects.<a href="./src/trellis/resources/projects.py">create</a>(\*\*<a href="src/trellis/types/project_create_params.py">params</a>) -> <a href="./src/trellis/types/project_create_response.py">ProjectCreateResponse</a></code>
- <code title="get /v1/projects">client.projects.<a href="./src/trellis/resources/projects.py">list</a>(\*\*<a href="src/trellis/types/project_list_params.py">params</a>) -> <a href="./src/trellis/types/project_list_response.py">ProjectListResponse</a></code>
- <code title="delete /v1/projects/{proj_id}">client.projects.<a href="./src/trellis/resources/projects.py">delete</a>(proj_id) -> <a href="./src/trellis/types/project_delete_response.py">ProjectDeleteResponse</a></code>

# Assets

Types:

```python
from trellis.types import Assets, AssetDeleteResponse
```

Methods:

- <code title="get /v1/assets">client.assets.<a href="./src/trellis/resources/assets.py">list</a>(\*\*<a href="src/trellis/types/asset_list_params.py">params</a>) -> <a href="./src/trellis/types/assets.py">Assets</a></code>
- <code title="delete /v1/assets/{asset_id}">client.assets.<a href="./src/trellis/resources/assets.py">delete</a>(asset_id) -> <a href="./src/trellis/types/asset_delete_response.py">AssetDeleteResponse</a></code>
- <code title="post /v1/assets/upload">client.assets.<a href="./src/trellis/resources/assets.py">upload</a>(\*\*<a href="src/trellis/types/asset_upload_params.py">params</a>) -> <a href="./src/trellis/types/assets.py">Assets</a></code>

# AssetsExtract

Types:

```python
from trellis.types import Extract
```

# Events

## Subscriptions

Types:

```python
from trellis.types.events import EventSubscription
```

### Actions

Types:

```python
from trellis.types.events.subscriptions import EventSubscriptionAction
```

## Actions

Types:

```python
from trellis.types.events import EventAction
```

## Jobs

Types:

```python
from trellis.types.events import Jobs
```

# Templates

Types:

```python
from trellis.types import Template, TemplateList
```

## Image

Types:

```python
from trellis.types.templates import TemplateImage
```

## Categories

Types:

```python
from trellis.types.templates import TemplateCategory
```
