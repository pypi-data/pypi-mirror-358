# Memories

Types:

```python
from supermemory.types import (
    MemoryUpdateResponse,
    MemoryAddResponse,
    MemoryGetResponse,
    MemoryUploadFileResponse,
)
```

Methods:

- <code title="patch /v3/memories/{id}">client.memories.<a href="./src/supermemory/resources/memories.py">update</a>(id, \*\*<a href="src/supermemory/types/memory_update_params.py">params</a>) -> <a href="./src/supermemory/types/memory_update_response.py">MemoryUpdateResponse</a></code>
- <code title="delete /v3/memories/{id}">client.memories.<a href="./src/supermemory/resources/memories.py">delete</a>(id) -> None</code>
- <code title="post /v3/memories">client.memories.<a href="./src/supermemory/resources/memories.py">add</a>(\*\*<a href="src/supermemory/types/memory_add_params.py">params</a>) -> <a href="./src/supermemory/types/memory_add_response.py">MemoryAddResponse</a></code>
- <code title="get /v3/memories/{id}">client.memories.<a href="./src/supermemory/resources/memories.py">get</a>(id) -> <a href="./src/supermemory/types/memory_get_response.py">MemoryGetResponse</a></code>
- <code title="post /v3/memories/file">client.memories.<a href="./src/supermemory/resources/memories.py">upload_file</a>(\*\*<a href="src/supermemory/types/memory_upload_file_params.py">params</a>) -> <a href="./src/supermemory/types/memory_upload_file_response.py">MemoryUploadFileResponse</a></code>

# Settings

Types:

```python
from supermemory.types import SettingUpdateResponse, SettingGetResponse
```

Methods:

- <code title="patch /v3/settings">client.settings.<a href="./src/supermemory/resources/settings.py">update</a>(\*\*<a href="src/supermemory/types/setting_update_params.py">params</a>) -> <a href="./src/supermemory/types/setting_update_response.py">SettingUpdateResponse</a></code>
- <code title="get /v3/settings">client.settings.<a href="./src/supermemory/resources/settings.py">get</a>() -> <a href="./src/supermemory/types/setting_get_response.py">SettingGetResponse</a></code>

# Connections

Types:

```python
from supermemory.types import ConnectionCreateResponse, ConnectionGetResponse
```

Methods:

- <code title="post /v3/connections/{provider}">client.connections.<a href="./src/supermemory/resources/connections.py">create</a>(provider, \*\*<a href="src/supermemory/types/connection_create_params.py">params</a>) -> <a href="./src/supermemory/types/connection_create_response.py">ConnectionCreateResponse</a></code>
- <code title="get /v3/connections/{connectionId}">client.connections.<a href="./src/supermemory/resources/connections.py">get</a>(connection_id) -> <a href="./src/supermemory/types/connection_get_response.py">ConnectionGetResponse</a></code>
