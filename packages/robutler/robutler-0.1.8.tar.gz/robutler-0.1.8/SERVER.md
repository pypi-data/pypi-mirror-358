# Robutler Server Implementation

## Overview

The Robutler server framework provides a clean, FastAPI-based server architecture for deploying AI agents with OpenAI-compatible endpoints. The implementation consists of two main classes:

- **`ServerBase`**: Core FastAPI server with agent decorators and lifecycle management
- **`Server`**: Enhanced server that extends ServerBase with automatic agent registration

## Architecture

### ServerBase (`robutler.server.base.ServerBase`)

The foundation class that provides:
- FastAPI server with middleware for request lifecycle management
- Agent decorator system for creating endpoints
- Request state management and context handling
- Lifecycle hooks (before_request, finalize_request)
- OpenAI-compatible streaming and non-streaming responses

### Server (`robutler.server.Server`)

A higher-level server that extends ServerBase with:
- Automatic agent registration from a list
- Simplified agent endpoint creation
- Built-in agent lifecycle management

## Key Features

### 1. Request Lifecycle Management

The server provides comprehensive request lifecycle hooks:

```python
@app.agent.before_request
async def before_handler(request):
    # Called before agent processing
    context = get_context()
    context.set("start_time", time.time())

@app.agent.finalize_request
async def finalize_handler(request, response):
    # Called after processing completes (including streaming)
    context = get_context()
    duration = time.time() - context.get("start_time", 0)
    print(f"Request took {duration}s")
```

### 2. Request State and Context

Each agent request gets a `RequestState` context:

```python
from robutler.server.base import get_context

@app.agent("my-agent")
async def my_agent(messages, stream=False):
    context = get_context()
    
    # Store data
    context.set("user_id", "123")
    
    # Track usage
    context.track_usage(
        credits=10,
        reason="Agent processing",
        metadata={"model": "gpt-4"}
    )
    
    return "Response"
```

### 3. OpenAI-Compatible Endpoints

Each agent automatically gets OpenAI-compatible endpoints:

- `POST /{agent-name}/chat/completions` - Chat completions (streaming & non-streaming)
- `GET /{agent-name}/chat/completions` - Endpoint info
- `POST /{agent-name}` - Control endpoint
- `GET /{agent-name}` - Agent info

### 4. Streaming Support

Full streaming support with proper lifecycle management:

```python
@app.agent("streaming-agent")
async def streaming_agent(messages, stream=False):
    if stream:
        # Return object with stream_events() method
        return StreamingResponse(...)
    else:
        return "Non-streaming response"
```

### 5. Pricing Decorator (Placeholder)

The framework includes a `@pricing` decorator for future cost tracking functionality:

```python
from robutler.server import pricing

@pricing(credits_per_request=10)
async def my_agent(messages, stream=False):
    return "Response"

@pricing(credits_per_token=0.1, max_credits=100)
async def token_based_agent(messages, stream=False):
    return "Response"
```

**Note**: The pricing decorator is currently a placeholder that stores pricing configuration but does not implement actual cost tracking. Future versions will integrate with the request lifecycle to track and enforce pricing.

## Environment Configuration

The server automatically loads environment variables from a `.env` file if present, making it easy to configure API keys and other settings.

### Setting up OpenAI API Key

For OpenAI agents to work, you need to configure your API key:

**Method 1: .env file (Recommended)**
```bash
# Create .env file in your project root
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

**Method 2: Environment variable**
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

**Method 3: Shell profile**
```bash
echo 'export OPENAI_API_KEY=your_openai_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Supported Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for OpenAI agents)
- `OPENAI_BASE_URL`: Custom OpenAI endpoint URL (optional)
- `OPENAI_ORGANIZATION`: OpenAI organization ID (optional)

### Dependencies

To use .env file support, install the optional dependency:
```bash
pip install python-dotenv
```

If `python-dotenv` is not installed, the server will still work but won't automatically load `.env` files.

## Usage Examples

### Basic ServerBase Usage

```python
from robutler.server.base import ServerBase

app = ServerBase()

@app.agent("assistant")
async def my_assistant(messages, stream=False):
    # Process messages
    response = f"You said: {messages[-1]['content']}"
    return response

# Add lifecycle hooks
@app.agent.before_request
async def log_request(request):
    print(f"Processing request to {request.url}")

@app.agent.finalize_request
async def log_completion(request, response):
    print("Request completed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### OpenAI Agent Usage

```python
from robutler.server import Server
from agents import Agent, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny and 72°F"

# Create OpenAI agents
weather_agent = Agent(
    name="weather-agent",
    instructions="You are a helpful weather assistant. Always respond in a friendly tone.",
    model="gpt-4o-mini",
    tools=[get_weather],
)

assistant_agent = Agent(
    name="assistant", 
    instructions="You are a helpful general assistant. Always respond in haiku form.",
    model="gpt-4o-mini",
)

# Create server with OpenAI agents
app = Server(agents=[weather_agent, assistant_agent])

# The server automatically detects OpenAI agents and uses Runner.run() to execute them
# Endpoints created: /weather-agent/chat/completions, /assistant/chat/completions
```

### Enhanced Server Usage

```python
from robutler.server import Server, pricing

class MyAgent:
    def __init__(self, name):
        self.name = name
    
    async def run(self, messages):
        return f"Agent {self.name}: {messages[-1]['content']}"
    
    async def run_streamed(self, messages):
        # Return streaming response
        pass

# Create agents
agents = [
    MyAgent("assistant"),
    MyAgent("translator"),
    MyAgent("summarizer")
]

# Create server with automatic agent registration
app = Server(agents=agents)

# Add global hooks
@app.agent.finalize_request
async def track_usage(request, response):
    context = get_context()
    if context:
        usage_data = context.usage
        print(f"Request used {usage_data.get('total_credits', 0)} credits")
```

### Dynamic Agent Resolution

```python
def resolve_agent(agent_name: str):
    # Return agent data or False if not found
    if agent_name in available_agents:
        return {"config": "...", "model": "gpt-4"}
    return False

@app.agent(resolve_agent)
async def dynamic_handler(messages, stream=False, agent_data=None):
    # agent_data contains the resolved data
    model = agent_data.get("model", "gpt-3.5-turbo")
    # Process with specific model
    return f"Processed with {model}"
```

## Request State API

### RequestState Class

```python
class RequestState:
    def __init__(self, request: Request)
    
    def set(self, key: str, value: Any) -> None
        """Store data in request context"""
    
    def get(self, key: str, default: Any = None) -> Any
        """Retrieve data from request context"""
    
    def track_usage(self, credits: int, reason: str, metadata: Dict = None) -> str
        """Track credit usage for this request"""
    
    @property
    def usage(self) -> Dict[str, Any]
        """Get all usage tracking data"""
    
    def get_duration(self) -> float
        """Get request duration in seconds"""
```

### Context Access

```python
from robutler.server.base import get_context

# In agent functions
context = get_context()
if context:
    context.set("key", "value")
    value = context.get("key")
```

## Streaming Implementation

### Streaming Response Format

The server supports OpenAI-compatible streaming with proper chunk format:

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion.chunk",
  "created": 1677652288,
  "model": "gpt-4",
  "choices": [{
    "index": 0,
    "delta": {
      "role": "assistant",
      "content": "Hello"
    },
    "finish_reason": null
  }]
}
```

Final chunks include finish_reason and usage information (when provided by the agent):

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion.chunk",
  "created": 1677652288,
  "model": "gpt-4",
  "choices": [{
    "index": 0,
    "delta": {},
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 15,
    "total_tokens": 40
  }
}
```

**Note**: The server does not generate fake usage statistics. Usage information is only included when provided by the actual agent implementation.

### Streaming Lifecycle

For streaming responses, the finalize callbacks are guaranteed to be called **after** streaming completes and receive the streaming response object:

```python
@app.agent.finalize_request
async def handle_streaming_completion(request, response):
    # For streaming responses, this is called after streaming completes
    # The response is a StreamingWrapper containing the original streaming response
    
    if hasattr(response, 'original_response'):
        print(f"Streaming completed for {request.url}")
        
    # The response object is passed directly without any data extraction
    # To access final chunks (like usage information), you can consume the response
    # or rely on the MockAgent's final chunk generation in tests
    
    # Example: The response is passed as-is to your callback
    # No intermediate parsing or data extraction is performed
```

## Agent Function Signatures

Agent functions support various parameter combinations:

```python
# Basic signature
async def agent(messages, stream=False):
    pass

# With context access
async def agent(messages, stream=False, context=None):
    pass

# With request access
async def agent(messages, stream=False, request=None):
    pass

# With dynamic agent data
async def agent(messages, stream=False, agent_data=None):
    pass

# Full signature
async def agent(messages, stream=False, context=None, request=None, agent_data=None):
    pass
```

## Error Handling

The server includes comprehensive error handling:

- Callback errors don't break requests
- Invalid request bodies return 422 status
- Agent function errors are caught and handled gracefully
- Streaming errors are properly formatted in response chunks

## Testing

The framework includes robust testing utilities with comprehensive test coverage:

```python
from robutler.server import Server
from robutler.tests.test_server import create_test_client

app = Server(agents=[my_agent])
client = create_test_client(app)

# Test non-streaming
response = client.post("/my-agent/chat/completions", json={
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": False
})

# Test streaming
response = client.post("/my-agent/chat/completions", json={
    "model": "gpt-4", 
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": True
})
```

### Test Coverage

The test suite includes 17 comprehensive tests covering:

- **Server Creation**: Basic initialization and inheritance
- **Agent Management**: Single and multiple agent registration
- **OpenAI Compatibility**: Response structure validation for streaming and non-streaming
- **Lifecycle Callbacks**: Before/finalize request hooks with proper timing
- **Streaming Lifecycle**: Verification that finalize callbacks receive the response after streaming completes
- **MockAgent Integration**: Tests verify that MockAgent generates proper final chunks with usage information

### MockAgent for Testing

The included MockAgent generates realistic OpenAI-compatible streaming responses:

```python
# MockAgent automatically generates:
# - Initial chunk with role: "assistant"
# - Content chunks with incremental text
# - Final chunk with finish_reason: "stop" and usage information
# - All in proper OpenAI streaming format
```

## Key Guarantees

1. **Single Callback Execution**: Finalize callbacks are called exactly once per request
2. **Streaming Completion**: For streaming responses, finalize callbacks are called after streaming completes
3. **Direct Response Access**: Finalize callbacks receive the StreamingWrapper response object directly
4. **Context Persistence**: Request context persists throughout the entire request lifecycle
5. **OpenAI Compatibility**: All responses follow OpenAI's chat completion format
6. **No Data Extraction**: The server does not parse or extract data from streaming responses
7. **Clean Architecture**: Simple, direct approach without intermediate data processing

## Performance Considerations

- Context variables are used for efficient request state management
- Streaming responses use async generators for memory efficiency
- Middleware is optimized to only run for agent endpoints
- Background tasks are supported for cleanup operations

## Migration from RobutlerServer

The new Server class replaces the old RobutlerServer with a cleaner API:

```python
# Old way
from robutler import RobutlerServer
server = RobutlerServer(agents=agents)

# New way
from robutler.server import Server
server = Server(agents=agents)
```

The new implementation provides the same functionality with better architecture, comprehensive testing, and improved lifecycle management. 