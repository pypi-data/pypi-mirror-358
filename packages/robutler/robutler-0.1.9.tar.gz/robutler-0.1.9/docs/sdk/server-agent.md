# Server & Agent Setup

Robutler provides two main components: `RobutlerAgent` for creating AI agents and `RobutlerServer` for serving them as OpenAI-compatible APIs.

## RobutlerAgent

Creates AI agents with automatic usage tracking and payment integration.

### Basic Usage

```python
from robutler.agent import RobutlerAgent

agent = RobutlerAgent(
    name="assistant",
    instructions="You are a helpful AI assistant.",
    credits_per_token=10,
    model="gpt-4o-mini"
)

# Use the agent
messages = [{"role": "user", "content": "Hello!"}]
response = await agent.run(messages=messages, stream=False)
print(response)
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `name` | `str` | Agent identifier (URL-safe) | Required |
| `instructions` | `str` | System instructions | Required |
| `credits_per_token` | `int` | Cost per token | `10` |
| `tools` | `List[Callable]` | Functions the agent can call | `[]` |
| `model` | `str` | OpenAI model | `"gpt-4o-mini"` |
| `intents` | `List[str]` | Descriptions for routing | `[]` |

## Enhanced Pricing Decorators

The `@pricing` decorator provides flexible tool pricing with three models:

### 1. Fixed Pricing

Use for tools with predictable costs:

```python
from robutler.agent import tool
from robutler.server import pricing

@tool
@pricing(credits_per_call=1000, reason="Time lookup service")
def get_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
@pricing(credits_per_call=5000)  # Uses default reason
def database_query(sql: str) -> list:
    """Execute database query."""
    return execute_sql(sql)
```

### 2. Dynamic Pricing

Use for variable costs based on usage:

```python
from robutler.server import pricing, Pricing

@tool
@pricing()  # No fixed cost - uses return value
def analyze_document(file_path: str) -> tuple:
    """Analyze document with usage-based pricing."""
    
    # Process document
    content = read_file(file_path)
    analysis = perform_analysis(content)
    
    # Calculate cost based on document size and complexity
    word_count = len(content.split())
    complexity = calculate_complexity(content)
    
    if complexity > 0.7:
        cost = word_count * 12  # Complex documents
        reason = f"Advanced analysis of complex {word_count}-word document"
        analysis_type = "advanced"
    else:
        cost = word_count * 6   # Simple documents
        reason = f"Standard analysis of {word_count}-word document"
        analysis_type = "standard"
    
    pricing_info = Pricing(
        credits=cost,
        reason=reason,
        metadata={
            "word_count": word_count,
            "complexity_score": complexity,
            "analysis_type": analysis_type,
            "file_path": file_path
        }
    )
    
    return analysis, pricing_info

@tool
@pricing()
def smart_search(query: str, depth: str = "basic") -> tuple:
    """Search with depth-based pricing."""
    
    if depth == "comprehensive":
        results = comprehensive_search(query)
        cost = len(results) * 50 + 2000  # Base cost + per-result
        reason = f"Comprehensive search: {len(results)} results for '{query}'"
    else:
        results = basic_search(query)
        cost = len(results) * 20 + 500   # Lower base + per-result
        reason = f"Basic search: {len(results)} results for '{query}'"
    
    pricing_info = Pricing(
        credits=cost,
        reason=reason,
        metadata={
            "query": query,
            "depth": depth,
            "results_count": len(results),
            "cost_per_result": 50 if depth == "comprehensive" else 20
        }
    )
    
    return results, pricing_info
```

### 3. Mixed Pricing (Base + Override)

Use base cost with conditional overrides:

```python
@tool
@pricing(credits_per_call=1500, reason="Base image processing")
def process_image(image_url: str, filters: list = None) -> Union[str, tuple]:
    """Process images with optional premium filters."""
    
    # Basic processing
    processed_url = apply_basic_processing(image_url)
    
    if filters and any(f in ["ai_enhance", "style_transfer", "upscale_4k"] for f in filters):
        # Premium processing - override base pricing
        premium_url = apply_premium_filters(processed_url, filters)
        
        # Calculate premium cost
        premium_cost = 1500  # Base cost
        for filter_name in filters:
            if filter_name == "ai_enhance":
                premium_cost += 3000
            elif filter_name == "style_transfer":
                premium_cost += 5000
            elif filter_name == "upscale_4k":
                premium_cost += 2000
        
        pricing_info = Pricing(
            credits=premium_cost,
            reason=f"Premium image processing with {', '.join(filters)}",
            metadata={
                "base_cost": 1500,
                "filters_applied": filters,
                "total_premium_cost": premium_cost - 1500,
                "image_url": image_url
            }
        )
        
        return premium_url, pricing_info
    
    # Use base pricing (1500 credits)
    return processed_url

@tool
@pricing(credits_per_call=800)
def translate_text(text: str, target_lang: str, quality: str = "standard") -> Union[str, tuple]:
    """Translate with quality-based pricing."""
    
    char_count = len(text)
    
    if quality == "professional" or char_count > 2000:
        # Professional or large translation
        result = professional_translate(text, target_lang)
        
        if char_count > 2000:
            cost = char_count * 2  # 2 credits per char for large texts
        else:
            cost = 3000  # Fixed professional rate
        
        pricing_info = Pricing(
            credits=cost,
            reason=f"Professional {target_lang} translation ({char_count} chars)",
            metadata={
                "character_count": char_count,
                "target_language": target_lang,
                "quality": quality,
                "rate_applied": "2 credits/char" if char_count > 2000 else "fixed_professional"
            }
        )
        
        return result, pricing_info
    
    # Standard translation uses base cost (800 credits)
    return standard_translate(text, target_lang)
```

### Agent with Enhanced Pricing Tools

```python
agent = RobutlerAgent(
    name="smart-assistant",
    instructions="You are an intelligent assistant with advanced tools.",
    tools=[get_time, analyze_document, smart_search, process_image, translate_text],
    credits_per_token=8,
    intents=[
        "I can analyze documents with intelligent pricing",
        "I can search with different depth levels",
        "I can process images with premium options",
        "I can translate with quality-based pricing"
    ]
)
```

## RobutlerServer

FastAPI server that automatically creates endpoints for agents.

### Automatic Endpoints

```python
from robutler.server import RobutlerServer
from robutler.agent import RobutlerAgent

# Create agents
assistant = RobutlerAgent(
    name="assistant",
    instructions="You are helpful",
    credits_per_token=5
)

# Create server - endpoints created automatically
app = RobutlerServer(agents=[assistant])

# Creates:
# POST /assistant/chat/completions - OpenAI chat completions
# GET  /assistant                  - Agent info
```

### Custom Agents with Dynamic Pricing

```python
app = RobutlerServer()

@app.agent("/weather/{location}")
@pricing()  # Dynamic pricing based on location complexity
async def weather_agent(request, location: str):
    """Custom weather agent with location-based pricing."""
    
    # Determine pricing based on location complexity
    weather_data = get_weather_data(location)
    data_points = len(weather_data.get('forecasts', []))
    
    if data_points > 10:
        # Detailed forecast
        cost = 2000
        reason = f"Detailed weather forecast for {location} ({data_points} data points)"
    else:
        # Basic forecast
        cost = 800
        reason = f"Basic weather forecast for {location}"
    
    # Generate response
    messages = request.messages
    system_msg = {
        "role": "system", 
        "content": f"You are a weather assistant for {location}. Weather data: {weather_data}"
    }
    messages.insert(0, system_msg)
    
    response = await process_weather_request(messages, location)
    
    # Return with pricing
    pricing_info = Pricing(
        credits=cost,
        reason=reason,
        metadata={
            "location": location,
            "data_points": data_points,
            "forecast_type": "detailed" if data_points > 10 else "basic"
        }
    )
    
    return response, pricing_info
```

### Usage Tracking Integration

Every request gets automatic usage tracking with detailed pricing information:

```python
from robutler.server import get_context

@app.finalize_request
async def log_detailed_usage(request, response, context):
    """Log detailed usage after request completion."""
    usage = context.usage
    
    print(f"=== Request Usage Report ===")
    print(f"Total Credits: {usage['total_credits']}")
    print(f"Operations: {usage['total_operations']}")
    print(f"Duration: {usage['duration_seconds']:.2f}s")
    
    # Log individual operations
    for operation in usage['receipt']['operations']:
        print(f"  - {operation['reason']}: {operation['credits']} credits")
        if operation.get('metadata'):
            print(f"    Metadata: {operation['metadata']}")
```

### Payment Integration

The server handles payment tokens automatically with detailed billing:

```python
# Client request with payment token
headers = {"X-Payment-Token": "pt_abc123..."}

# Server automatically:
# 1. Validates token has sufficient balance
# 2. Tracks all tool usage with pricing details
# 3. Charges credits after request completion
# 4. Provides detailed usage breakdown
# 5. Returns 402 if insufficient funds with usage summary
```

### Running the Server

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

The server provides OpenAI-compatible endpoints with automatic payment handling, intelligent pricing, and comprehensive usage tracking. 