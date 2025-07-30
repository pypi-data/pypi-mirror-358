# Weavium Python Client

A Python client library for the Weavium API, enabling you to compress prompts and inject data into datasets with ease.

## Features

- **Prompt Compression**: Reduce token usage by compressing your prompts while maintaining semantic meaning
- **Data Injection**: Inject conversation data into Weavium datasets for analysis and processing
- **Easy Integration**: Simple, object-oriented interface for all API operations
- **Type Safety**: Full type hints and dataclass support for better development experience

## Installation

```bash
pip install weavium
```

## Quick Start

### Setup

First, you'll need a Weavium API key. You can get one from the [Weavium dashboard](https://app.weavium.com).

```python
import os
from weavium import WeaviumClient

# Option 1: Set environment variable
os.environ['WEAVIUM_API_KEY'] = 'your-api-key-here'
client = WeaviumClient()

# Option 2: Pass API key directly
client = WeaviumClient(api_key='your-api-key-here')
```

### Compressing Prompts

```python
from weavium import WeaviumClient, CompressionChunkStrategy

client = WeaviumClient()

# Create messages
messages = [
    {"role": "system", "content": "You are a helpful assistant that answers questions about Python programming."},
    {"role": "user", "content": "Can you explain how to use list comprehensions in Python? I want to understand the syntax and see some examples of how they can make code more concise and readable."}
]

# Compress the conversation
result = client.compress(
    messages=messages,
    compression_rate=0.3,  # Target 30% of original size
    chunk_strategy=CompressionChunkStrategy.NONE
)

print(f"Original tokens: {result.original_tokens}")
print(f"Compressed tokens: {result.compressed_tokens}")
print(f"Compression rate: {result.compression_rate}")
print(f"Compressed content: {result.messages[-1].content}")
```

### Injecting Data

```python
# Inject conversation data into a dataset
messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "How do I create a list in Python?"},
    {"role": "user", "content": "What's the difference between lists and tuples?"}
]

inject_result = client.inject(messages=messages)

print(f"Dataset ID: {inject_result.dataset_id}")
print(f"Items created: {inject_result.items_created}")
```

### Using Helper Methods

```python
# Create messages using helper methods
client = WeaviumClient()

messages = [
    client.create_system_message("You are a helpful assistant."),
    client.create_user_message("What is machine learning?"),
    client.create_assistant_message("Machine learning is a subset of AI...")
]

result = client.compress(messages=messages)
```

## API Reference

### WeaviumClient

The main client class for interacting with the Weavium API.

#### Constructor

```python
WeaviumClient(
    api_key: Optional[str] = None,
    base_url: str = "https://api.weavium.com",
    timeout: int = 30
)
```

- `api_key`: Your Weavium API key. If not provided, looks for `WEAVIUM_API_KEY` environment variable.
- `base_url`: Base URL for the Weavium API.
- `timeout`: Request timeout in seconds.

#### Methods

##### compress()

Compress a conversation using the Weavium compression algorithm.

```python
compress(
    messages: List[Union[LLMMessage, Dict[str, str]]],
    compression_rate: float = 0.2,
    chunk_strategy: Union[CompressionChunkStrategy, str] = CompressionChunkStrategy.NONE
) -> CompressionResult
```

**Parameters:**
- `messages`: List of conversation messages
- `compression_rate`: Target compression rate (0.0 to 1.0)
- `chunk_strategy`: Chunking strategy for compression

**Returns:** `CompressionResult` object with compressed messages and metadata.

##### inject()

Inject messages into a Weavium dataset.

```python
inject(
    messages: List[Union[LLMMessage, Dict[str, str]]],
    dataset_id: Optional[str] = None
) -> InjectResult
```

**Parameters:**
- `messages`: List of messages to inject
- `dataset_id`: Optional dataset ID. If not provided, creates dataset based on system prompt.

**Returns:** `InjectResult` object with dataset information.

### Data Classes

#### LLMMessage

Represents a message in a conversation.

```python
@dataclass
class LLMMessage:
    role: str      # Message role (system, user, assistant)
    content: str   # Message content
```

#### CompressionResult

Result of a compression operation.

```python
@dataclass
class CompressionResult:
    messages: List[LLMMessage]    # Compressed messages
    compression_rate: str         # Achieved compression rate
    original_tokens: int          # Original token count
    compressed_tokens: int        # Compressed token count
```

#### InjectResult

Result of an inject operation.

```python
@dataclass
class InjectResult:
    dataset_id: str              # Dataset ID
    dataset_name: str            # Dataset name
    items_created: int           # Number of items created
    system_prompt_hash: str      # Hash of system prompt
```

### Enums

#### CompressionChunkStrategy

Available compression chunking strategies.

```python
class CompressionChunkStrategy(Enum):
    NONE = "none"
    SLIDING_WINDOW = "sliding_window"
    SEMANTIC = "semantic"
```

## Error Handling

The client raises standard Python exceptions:

```python
from weavium import WeaviumClient
import requests

client = WeaviumClient()

try:
    result = client.compress(messages=[])
except ValueError as e:
    print(f"Invalid input: {e}")
except requests.RequestException as e:
    print(f"API request failed: {e}")
```

## Environment Variables

- `WEAVIUM_API_KEY`: Your Weavium API key

## Development

To set up for development:

```bash
git clone https://github.com/weavium/weavium-python-client
cd weavium-python-client
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Documentation: [https://docs.weavium.com](https://docs.weavium.com)
- Issues: [GitHub Issues](https://github.com/weavium/weavium-python-client/issues)
- Email: support@weavium.com 