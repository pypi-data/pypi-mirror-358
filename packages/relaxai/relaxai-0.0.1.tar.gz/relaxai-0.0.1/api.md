# Chat

Types:

```python
from relaxai.types import (
    ChatCompletionMessage,
    ContentFilterResults,
    FunctionCall,
    FunctionDefinition,
    Usage,
    ChatCreateCompletionResponse,
)
```

Methods:

- <code title="post /v1/chat/completions">client.chat.<a href="./src/relaxai/resources/chat.py">create_completion</a>(\*\*<a href="src/relaxai/types/chat_create_completion_params.py">params</a>) -> <a href="./src/relaxai/types/chat_create_completion_response.py">ChatCreateCompletionResponse</a></code>

# Embeddings

Types:

```python
from relaxai.types import EmbeddingCreateResponse
```

Methods:

- <code title="post /v1/embeddings">client.embeddings.<a href="./src/relaxai/resources/embeddings.py">create</a>(\*\*<a href="src/relaxai/types/embedding_create_params.py">params</a>) -> <a href="./src/relaxai/types/embedding_create_response.py">EmbeddingCreateResponse</a></code>

# Health

Types:

```python
from relaxai.types import HealthCheckResponse
```

Methods:

- <code title="get /v1/health">client.health.<a href="./src/relaxai/resources/health.py">check</a>() -> str</code>

# Models

Types:

```python
from relaxai.types import Model, ModelListResponse
```

Methods:

- <code title="get /v1/models/{model}">client.models.<a href="./src/relaxai/resources/models.py">retrieve</a>(model) -> <a href="./src/relaxai/types/model.py">Model</a></code>
- <code title="get /v1/models">client.models.<a href="./src/relaxai/resources/models.py">list</a>() -> <a href="./src/relaxai/types/model_list_response.py">ModelListResponse</a></code>
