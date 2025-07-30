# Shared Types

```python
from mpx_genai_sdk.types import CreateResponseObject, GenerateResponseObject
```

# ConnectionTest

Types:

```python
from mpx_genai_sdk.types import ConnectionTestRetrieveResponse
```

Methods:

- <code title="get /connection/test">client.connection_test.<a href="./src/mpx_genai_sdk/resources/connection_test.py">retrieve</a>() -> str</code>

# Functions

Methods:

- <code title="post /functions/general">client.functions.<a href="./src/mpx_genai_sdk/resources/functions.py">create_general</a>(\*\*<a href="src/mpx_genai_sdk/types/function_create_general_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/generate_response_object.py">GenerateResponseObject</a></code>
- <code title="post /functions/imageto3d">client.functions.<a href="./src/mpx_genai_sdk/resources/functions.py">imageto3d</a>(\*\*<a href="src/mpx_genai_sdk/types/function_imageto3d_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/generate_response_object.py">GenerateResponseObject</a></code>

# Components

Methods:

- <code title="post /components/optimize">client.components.<a href="./src/mpx_genai_sdk/resources/components.py">optimize</a>(\*\*<a href="src/mpx_genai_sdk/types/component_optimize_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/create_response_object.py">CreateResponseObject</a></code>
- <code title="post /components/text2image">client.components.<a href="./src/mpx_genai_sdk/resources/components.py">text2image</a>(\*\*<a href="src/mpx_genai_sdk/types/component_text2image_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/generate_response_object.py">GenerateResponseObject</a></code>

# Llms

Methods:

- <code title="post /llm/llm_call">client.llms.<a href="./src/mpx_genai_sdk/resources/llms.py">call</a>(\*\*<a href="src/mpx_genai_sdk/types/llm_call_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/generate_response_object.py">GenerateResponseObject</a></code>
- <code title="post /llm/image_query">client.llms.<a href="./src/mpx_genai_sdk/resources/llms.py">image_query</a>(\*\*<a href="src/mpx_genai_sdk/types/llm_image_query_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/generate_response_object.py">GenerateResponseObject</a></code>

# Assets

Methods:

- <code title="post /assets/create">client.assets.<a href="./src/mpx_genai_sdk/resources/assets.py">create</a>(\*\*<a href="src/mpx_genai_sdk/types/asset_create_params.py">params</a>) -> <a href="./src/mpx_genai_sdk/types/shared/create_response_object.py">CreateResponseObject</a></code>

# Status

Types:

```python
from mpx_genai_sdk.types import StatusResponseObject
```

Methods:

- <code title="get /status/{requestId}">client.status.<a href="./src/mpx_genai_sdk/resources/status.py">retrieve</a>(request_id) -> <a href="./src/mpx_genai_sdk/types/status_response_object.py">StatusResponseObject</a></code>
