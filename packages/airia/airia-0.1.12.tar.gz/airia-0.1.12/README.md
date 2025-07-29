# Airia Python API Library

[![PyPI version](https://badge.fury.io/py/airia.svg)](https://badge.fury.io/py/airia)
[![Python versions](https://img.shields.io/pypi/pyversions/airia.svg)](https://pypi.org/project/airia/)
[![License](https://img.shields.io/pypi/l/airia.svg)](https://pypi.org/project/airia/)

Airia Python API Library that provides a clean and intuitive interface to interact with the Airia AI platform API. The library offers both synchronous and asynchronous clients for maximum flexibility in your applications.

## Features

- **Dual Client Support**: Choose between synchronous (`AiriaClient`) and asynchronous (`AiriaAsyncClient`) implementations
- **Pipeline Execution**: Easily run AI pipelines with customizable parameters
- **Gateway Support**: Seamlessly integrate with OpenAI and Anthropic services through Airia gateways
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Logging**: Built-in configurable logging with correlation ID support for request tracing
- **Flexible Authentication**: Support for both API keys and bearer tokens with flexible configuration
- **API Key Management**: API key configuration via parameters or environment variables
- **Bearer Token Support**: Bearer token authentication for ephemeral, short-lived credentials

## Installation

You can install the package using pip or uv:

<table>
<tr>
<th>pip</th>
<th>uv</th>
</tr>
<tr>
<td>

```bash
pip install airia
```

</td>
<td>

```bash
uv add airia
```

</td>
</tr>
</table>

### Install with optional dependencies

The package supports optional dependencies for gateway functionality:

<table>
<tr>
<th>OpenAI Gateway</th>
<th>Anthropic Gateway</th>
<th>All Gateways</th>
</tr>
<tr>
<td>

```bash
pip install "airia[openai]"
```

</td>
<td>

```bash
pip install "airia[anthropic]"
```

</td>
<td>

```bash
pip install "airia[all]"
```

</td>
</tr>
</table>

### Install with development dependencies

Clone the repository:

```bash
git clone https://github.com/AiriaLLC/airia-python.git
cd airia-python
```

Then, run one of the following commands:

<table>
<tr>
<th>pip</th>
<th>uv</th>
</tr>
<tr>
<td>

```bash
pip install dependency-groups
dev=$(python -m dependency_groups dev)
pip install -e .
pip install $dev
```

</td>
<td>

```bash
uv sync --frozen --group dev
```

</td>
</tr>
</table>

## Building from Source

First make sure you have already cloned the repository, then run one of the following commands:

<table>
<tr>
<th>pip</th>
<th>uv</th>
</tr>
<tr>
<td>

```bash
pip install build
python -m build
```

</td>
<td>

```bash
uv build
```

</td>
</tr>
</table>

This will create both wheel and source distribution in the `dist/` directory.

## Quick Start

### Client Instantiation

```python
from airia import AiriaClient

# API Key Authentication
client = AiriaClient(
    base_url="https://api.airia.ai",        # Default: "https://api.airia.ai"
    api_key=None,                           # Or set AIRIA_API_KEY environment variable
    timeout=30.0,                           # Request timeout in seconds (default: 30.0)
    log_requests=False,                     # Enable request/response logging (default: False)
    custom_logger=None                      # Use custom logger (default: None - uses built-in)
)

# Bearer Token Authentication
client = AiriaClient(
    base_url="https://api.airia.ai",        # Default: "https://api.airia.ai"
    bearer_token="your_bearer_token",       # Must be provided explicitly (no env var fallback)
    timeout=30.0,                           # Request timeout in seconds (default: 30.0)
    log_requests=False,                     # Enable request/response logging (default: False)
    custom_logger=None                      # Use custom logger (default: None - uses built-in)
)

# Convenience method for bearer token
client = AiriaClient.with_bearer_token(
    bearer_token="your_bearer_token",
    base_url="https://api.airia.ai",        # Optional, uses default if not provided
    timeout=30.0,                           # Optional, uses default if not provided
    log_requests=False,                     # Optional, uses default if not provided
    custom_logger=None                      # Optional, uses default if not provided
)
```

### Synchronous Usage

#### With API Key

```python
from airia import AiriaClient

# Initialize client (API key can be passed directly or via AIRIA_API_KEY environment variable)
client = AiriaClient(api_key="your_api_key")

# Execute a pipeline
response = client.execute_pipeline(
    pipeline_id="your_pipeline_id",
    user_input="Tell me about quantum computing"
)

print(response.result)
```

#### With Bearer Token

```python
from airia import AiriaClient

# Initialize client with bearer token
client = AiriaClient.with_bearer_token(bearer_token="your_bearer_token")

# Execute a pipeline
response = client.execute_pipeline(
    pipeline_id="your_pipeline_id",
    user_input="Tell me about quantum computing"
)

print(response.result)
```

#### Synchronous Streaming

```python
from airia import AiriaClient

# Initialize client (API key can be passed directly or via AIRIA_API_KEY environment variable)
client = AiriaClient(api_key="your_api_key")
# Or with bearer token: client = AiriaClient.with_bearer_token(bearer_token="your_bearer_token")

# Execute a pipeline
response = client.execute_pipeline(
    pipeline_id="your_pipeline_id",
    user_input="Tell me about quantum computing",
    async_output=True
)

for c in response.stream:
    print(c)
```

### Asynchronous Usage

#### With API Key

```python
import asyncio
from airia import AiriaAsyncClient

async def main():
    client = AiriaAsyncClient(api_key="your_api_key")
    response = await client.execute_pipeline(
        pipeline_id="your_pipeline_id",
        user_input="Tell me about quantum computing"
    )
    print(response.result)

asyncio.run(main())
```

#### With Bearer Token

```python
import asyncio
from airia import AiriaAsyncClient

async def main():
    client = AiriaAsyncClient.with_bearer_token(bearer_token="your_bearer_token")
    response = await client.execute_pipeline(
        pipeline_id="your_pipeline_id",
        user_input="Tell me about quantum computing"
    )
    print(response.result)

asyncio.run(main())
```

#### Asynchronous Streaming

```python
import asyncio
from airia import AiriaAsyncClient

async def main():
    client = AiriaAsyncClient(api_key="your_api_key")
    # Or with bearer token: client = AiriaAsyncClient.with_bearer_token(bearer_token="your_bearer_token")
    response = await client.execute_pipeline(
        pipeline_id="your_pipeline_id",
        user_input="Tell me about quantum computing",
        async_output=True
    )
    async for c in response.stream:
        print(c)

asyncio.run(main())
```

## Streaming Event Parsing

When using streaming mode (`async_output=True`), the API returns Server-Sent Events (SSE) that contain different types of messages throughout the pipeline execution. You can parse and filter these events to extract specific information.

### Available Message Types

The streaming response includes various message types defined in `airia.types.sse`. Here are the key ones:

- `AgentModelStreamFragmentMessage` - Contains actual LLM output chunks
- `AgentModelStreamStartMessage` - Indicates LLM streaming has started
- `AgentModelStreamEndMessage` - Indicates LLM streaming has ended
- `AgentStepStartMessage` - Indicates a pipeline step has started
- `AgentStepEndMessage` - Indicates a pipeline step has ended
- `AgentOutputMessage` - Contains step output

<details>
<summary>Click to expand the full list of message types</summary>

```python
[
    AgentPingMessage,
    AgentStartMessage,
    AgentEndMessage,
    AgentStepStartMessage,
    AgentStepHaltMessage,
    AgentStepEndMessage,
    AgentOutputMessage,
    AgentAgentCardMessage,
    AgentDatasearchMessage,
    AgentInvocationMessage,
    AgentModelMessage,
    AgentPythonCodeMessage,
    AgentToolActionMessage,
    AgentModelStreamStartMessage,
    AgentModelStreamEndMessage,
    AgentModelStreamErrorMessage,
    AgentModelStreamUsageMessage,
    AgentModelStreamFragmentMessage,
    AgentAgentCardStreamStartMessage,
    AgentAgentCardStreamErrorMessage,
    AgentAgentCardStreamFragmentMessage,
    AgentAgentCardStreamEndMessage,
    AgentToolRequestMessage,
    AgentToolResponseMessage,
]
```

</details>

### Filtering LLM Output

To extract only the actual LLM output text from the stream:

```python
from airia import AiriaClient
from airia.types import AgentModelStreamFragmentMessage

client = AiriaClient(api_key="your_api_key")
# Or with bearer token: client = AiriaClient.with_bearer_token(bearer_token="your_bearer_token")

response = client.execute_pipeline(
    pipeline_id="your_pipeline_id",
    user_input="Tell me about quantum computing",
    async_output=True
)

# Filter and display only LLM output
for event in response.stream:
    if isinstance(event, AgentModelStreamFragmentMessage) and event.index != -1:
        print(event.content, end="", flush=True)
```

## Pipeline Configuration Retrieval

You can retrieve detailed configuration information about a pipeline using the `get_pipeline_config` method:

> To get a list of all active pipeline ids, run the `get_active_pipelines_ids` method.

```python
from airia import AiriaClient

client = AiriaClient(api_key="your_api_key")
# Or with bearer token: client = AiriaClient.with_bearer_token(bearer_token="your_bearer_token")

# Get pipeline configuration
config = client.get_pipeline_config(pipeline_id="your_pipeline_id")

# Access configuration details
print(f"Pipeline Name: {config.agent.name}")
```

## Conversation Management

You can create and manage conversations using the `create_conversation` method. Conversations allow you to organize and persist interactions within the Airia platform.

### Creating Conversations

#### Synchronous Usage

```python
from airia import AiriaClient

client = AiriaClient(api_key="your_api_key")
# Or with bearer token: client = AiriaClient.with_bearer_token(bearer_token="your_bearer_token")

# Create a basic conversation
conversation = client.create_conversation(
    user_id="user_123"
)
print(f"Created conversation: {conversation.conversation_id}")
print(f"WebSocket URL: {conversation.websocket_url}")

# Create a conversation with all options
conversation = client.create_conversation(
    user_id="user_123",
    title="My Research Session",
    deployment_id="deployment_456", 
    data_source_files={"documents": ["doc1.pdf", "doc2.txt"]},
    is_bookmarked=True
)
print(f"Created bookmarked conversation: {conversation.conversation_id}")
```

#### Asynchronous Usage

```python
import asyncio
from airia import AiriaAsyncClient

async def main():
    client = AiriaAsyncClient(api_key="your_api_key")
    # Or with bearer token: client = AiriaAsyncClient.with_bearer_token(bearer_token="your_bearer_token")
    
    # Create a basic conversation
    conversation = await client.create_conversation(
        user_id="user_123"
    )
    print(f"Created conversation: {conversation.conversation_id}")
    
    # Create a conversation with all options
    conversation = await client.create_conversation(
        user_id="user_123",
        title="My Research Session",
        deployment_id="deployment_456",
        data_source_files={"documents": ["doc1.pdf", "doc2.txt"]},
        is_bookmarked=True
    )
    print(f"Created bookmarked conversation: {conversation.conversation_id}")

asyncio.run(main())
```

### Conversation Parameters

- **user_id** (required): The unique identifier of the user creating the conversation
- **title** (optional): A descriptive title for the conversation
- **deployment_id** (optional): The unique identifier of the deployment to associate with the conversation
- **data_source_files** (optional): Configuration for data source files to be associated with the conversation
- **is_bookmarked** (optional): Whether the conversation should be bookmarked (defaults to False)
- **correlation_id** (optional): A unique identifier for request tracing and logging

### Response Fields

The `create_conversation` method returns a `CreateConversationResponse` object containing:

- **conversation_id**: The unique identifier of the created conversation
- **user_id**: The user ID associated with the conversation
- **websocket_url**: The WebSocket URL for real-time communication
- **deployment_id**: The deployment ID associated with the conversation
- **icon_id** and **icon_url**: Optional conversation icon information
- **description**: Optional conversation description
- **space_name**: Optional workspace or space name

## Authentication Methods

Airia supports two authentication methods:

### API Keys
- Can be passed as a parameter or via `AIRIA_API_KEY` environment variable
- Support gateway functionality (OpenAI and Anthropic gateways)
- Suitable for long-term, persistent authentication

### Bearer Tokens
- Must be provided explicitly (no environment variable fallback)
- **Important**: Bearer tokens cannot be used with gateway functionality
- Suitable for ephemeral, short-lived authentication scenarios
- Ideal for temporary access or programmatic token generation

```python
# ✅ API key with gateway support
client = AiriaClient.with_openai_gateway(api_key="your_api_key")

# ❌ Bearer token with gateway - NOT SUPPORTED
# client = AiriaClient.with_openai_gateway(bearer_token="token")  # This won't work
```

## Gateway Usage

Airia provides gateway capabilities for popular AI services like OpenAI and Anthropic, allowing you to use your Airia API key with these services.

> **Note**: Gateway functionality requires API key authentication. Bearer tokens are not supported for gateway usage.

### OpenAI Gateway

```python
from airia import AiriaClient

# Initialize client with OpenAI gateway support
client = AiriaClient.with_openai_gateway(api_key="your_airia_api_key")

# Use OpenAI's API through Airia's gateway
response = client.openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ]
)

print(response.choices[0].message.content)
```

### Anthropic Gateway

```python
from airia import AiriaClient

# Initialize client with Anthropic gateway support
client = AiriaClient.with_anthropic_gateway(api_key="your_airia_api_key")

# Use Anthropic's API through Airia's gateway
response = client.anthropic.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.content[0].text)
```

You can set the Gateway URL by passing the `gateway_url` parameter when using the gateway constructors. The default values are `https://gateway.airia.ai/openai/v1` for OpenAI and `https://gateway.airia.ai/anthropic` for Anthropic.

### Asynchronous Gateway Usage

Both gateways also support asynchronous usage:

```python
import asyncio
from airia import AiriaAsyncClient

async def main():
    # Initialize async client with gateway support
    client = AiriaAsyncClient.with_openai_gateway(api_key="your_airia_api_key")
    
    # Use OpenAI's API asynchronously through Airia's gateway
    response = await client.openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
    )
    
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Advanced Usage

### Pipeline Execution with All Options

```python
response = client.execute_pipeline(
    pipeline_id="pipeline_id",
    user_input="Your input text",
    debug=True,                          # Enable debug mode
    user_id="user_guid",                 # User identifier 
    conversation_id="conversation_guid", # Conversation identifier
    async_output=False,                  # Stream response (async mode)
    include_tools_response=True,         # Return the initial LLM tool result
    images=["base64_encoded_image"],     # Include image data
    files=["base64_encoded_file"],       # Include file data
    data_source_folders={},              # Data source folders configuration
    data_source_files={},                # Data source files configuration
    in_memory_messages=[                 # Context messages for conversation
        {"role": "user", "message": "Previous message"}
    ],
    current_date_time="2025-03-26T21:00:00", # Override current date/time
    save_history=True,                   # Save to conversation history
    additional_info=["extra data"],      # Additional metadata
    prompt_variables={"var1": "value1"}, # Variables for prompt templating
    correlation_id="request-123",        # Request tracing ID
    api_version="v2"                     # API version for the request
)
```

### Configuring Logging

```python
import sys
from airia import configure_logging

# Basic configuration
logger = configure_logging()

# Advanced configuration
file_logger = configure_logging(
    format_string="[{time:YYYY-MM-DD HH:mm:ss}] [{level}] {message}",
    level="DEBUG",
    sink="app.log",
    rotation="10 MB",
    retention="1 week",
    include_correlation_id=True
)

# Console output with custom format
console_logger = configure_logging(
    format_string="[{time:HH:mm:ss}] {message}",
    level="INFO",
    sink=sys.stdout
)
```

## Error Handling

The SDK uses custom exceptions to provide clear error messages:

```python
from airia import AiriaAPIError, AiriaClient

# Works with both API keys and bearer tokens
client = AiriaClient(api_key="your_api_key")
# Or: client = AiriaClient.with_bearer_token(bearer_token="your_bearer_token")

try:
    response = client.execute_pipeline(
        pipeline_id="invalid_id",
        user_input="test"
    )
except AiriaAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

## Requirements

- Python 3.9 or higher
- Core dependencies:
  - requests
  - aiohttp
  - loguru
  - pydantic

- Optional dependencies:
  - OpenAI gateway: `openai>=1.74.0`
  - Anthropic gateway: `anthropic>=0.49.0`

## Development

To run tests (make sure you have development dependencies installed):

```bash
pytest
```

For testing gateway functionality, install the optional dependencies:

```bash
# For OpenAI gateway tests
pip install -e .[openai]
pytest tests/test_openai_gateway.py

# For Anthropic gateway tests
pip install -e .[anthropic]
pytest tests/test_anthropic_gateway.py

# For all tests
pip install -e .[all]
pytest
```
