# Payment System

Robutler includes a credit-based payment system that enables agent-to-agent transactions and usage tracking. Agents can earn credits by providing services and spend credits to access other agents that require payment for their services.

## Agent Pricing Arguments

Set pricing when creating agents with `RobutlerAgent`:

```python
from robutler import RobutlerAgent

# Per-token pricing (variable cost)
assistant = RobutlerAgent(
    name="assistant",
    instructions="You are a helpful AI assistant",
    credits_per_token=10,  # 10 credits per output token
    model="gpt-4o-mini"
)

# Free agent (no pricing)
free_agent = RobutlerAgent(
    name="free-helper",
    instructions="You provide free assistance",
    # No credits_per_token = free to use
    model="gpt-4o-mini"
)
```

**Arguments:** The `credits_per_token` parameter sets credits charged per output token (omit for free agents). All standard agent arguments like `name`, `instructions`, `model`, and `intents` are also available.

## Enhanced Pricing Decorators

The `@pricing` decorator provides flexible function-level billing with three pricing models:

### Fixed Pricing

Use `@pricing(credits_per_call=X)` for functions with predictable costs:

```python
from robutler.server import pricing
from robutler.agent import tool

@tool()
@pricing(credits_per_call=1000, reason="Weather API lookup")
def get_weather(location: str) -> str:
    """Weather lookup - 1000 credits per call"""
    return f"Weather in {location}: Sunny, 72°F"

@tool()
@pricing(credits_per_call=5000)  # Default reason: "Function 'database_query' called"
def database_query(sql: str) -> list:
    """Database query - 5000 credits per call"""
    return execute_query(sql)
```

### Dynamic Pricing

Use `@pricing()` with return value tuples for variable costs:

```python
from robutler.server import pricing, Pricing

@tool()
@pricing()  # No fixed pricing, uses return value
def generate_report(data: str) -> tuple:
    """Report generation - variable cost based on complexity"""
    result = create_detailed_report(data)
    
    # Calculate cost based on data complexity
    processing_cost = len(data) * 15 + analyze_complexity(data) * 100
    
    pricing_info = Pricing(
        credits=processing_cost,
        reason=f"Generated {len(result)} character report from {len(data)} character input",
        metadata={
            "input_length": len(data),
            "output_length": len(result),
            "complexity_score": analyze_complexity(data),
            "rate_per_char": 15
        }
    )
    
    return result, pricing_info

@tool()
@pricing()
def ai_analysis(text: str) -> tuple:
    """AI analysis with usage-based pricing"""
    
    if len(text) > 1000:
        # Complex analysis
        result = advanced_ai_analysis(text)
        cost = len(text) * 20
        reason = f"Advanced AI analysis of {len(text)} characters"
        complexity = "high"
    else:
        # Simple analysis
        result = basic_ai_analysis(text)
        cost = len(text) * 5
        reason = f"Basic AI analysis of {len(text)} characters"
        complexity = "low"
    
    pricing_info = Pricing(
        credits=cost,
        reason=reason,
        metadata={
            "analysis_type": complexity,
            "input_size": len(text),
            "cost_per_char": 20 if complexity == "high" else 5
        }
    )
    
    return result, pricing_info
```

### Mixed Pricing (Base + Override)

Use `@pricing(credits_per_call=X)` with conditional return tuples:

```python
@tool()
@pricing(credits_per_call=500, reason="Base image processing")
def process_image(image_data: bytes, enhance: bool = False) -> Union[bytes, tuple]:
    """Image processing with optional enhancement"""
    
    # Basic processing
    result = basic_image_processing(image_data)
    
    if enhance:
        # Premium enhancement - override base pricing
        enhanced_result = premium_enhancement(result)
        
        pricing_info = Pricing(
            credits=2500,  # Override the 500 base cost
            reason="Premium image enhancement applied",
            metadata={
                "service_tier": "premium",
                "base_cost": 500,
                "enhancement_cost": 2000,
                "image_size": len(image_data)
            }
        )
        
        return enhanced_result, pricing_info
    
    # Use base pricing (500 credits from decorator)
    return result

@tool() 
@pricing(credits_per_call=1000)
def smart_translation(text: str, target_lang: str, quality: str = "standard") -> Union[str, tuple]:
    """Translation with quality-based pricing"""
    
    if quality == "premium":
        # Premium translation with custom pricing
        result = premium_translate(text, target_lang)
        
        pricing_info = Pricing(
            credits=len(text) * 10,  # Premium rate
            reason=f"Premium translation to {target_lang} ({len(text)} chars)",
            metadata={
                "quality": "premium",
                "target_language": target_lang,
                "character_count": len(text),
                "rate": "10 credits/char"
            }
        )
        
        return result, pricing_info
    
    # Standard translation uses base cost (1000 credits)
    return standard_translate(text, target_lang)
```

### Pricing Model Reference

The `Pricing` model for dynamic pricing:

```python
from robutler.server import Pricing

pricing_info = Pricing(
    credits=1500,                    # Required: Number of credits to charge
    reason="Custom processing task",  # Required: Human-readable explanation
    metadata={                       # Optional: Additional tracking data
        "processing_type": "premium",
        "input_size": 1024,
        "output_size": 2048,
        "rate_per_byte": 1.5
    }
)
```

### Usage Tracking Integration

All pricing decorators automatically integrate with Robutler's usage tracking system:

```python
from robutler.server import get_context

@tool()
@pricing(credits_per_call=750)
def api_call_with_tracking(endpoint: str) -> str:
    """API call with automatic usage tracking"""
    
    # The decorator automatically tracks:
    # - 750 credits charged
    # - Function name and timestamp
    # - Request context information
    
    result = make_external_api_call(endpoint)
    
    # Access current usage in function if needed
    context = get_context()
    if context:
        print(f"Total credits used so far: {context.usage['total_credits']}")
    
    return result
```

### Async Function Support

The pricing decorator works seamlessly with async functions:

```python
@tool()
@pricing(credits_per_call=2000)
async def async_api_call(data: dict) -> str:
    """Async function with pricing"""
    result = await external_async_api(data)
    return result

@tool()
@pricing()
async def async_variable_pricing(query: str) -> tuple:
    """Async function with dynamic pricing"""
    result = await complex_async_processing(query)
    
    pricing_info = Pricing(
        credits=len(result) * 8,
        reason=f"Async processing generated {len(result)} characters",
        metadata={"async": True, "query_length": len(query)}
    )
    
    return result, pricing_info
```

## Payment Tokens

Payment tokens enable secure, controlled access to paid agents and services. They are used to grant clients or other agents spending authorization without sharing your main account credentials. Common use cases include providing API access to customers, enabling agent-to-agent transactions, and setting spending limits for automated systems.

**Payment tokens** contain a credit balance and are used for all transactions:

1. **Client requests service** with payment token in `X-Payment-Token` header
2. **Agent processes request** and calculates cost (tokens × rate or fixed cost)
3. **Platform validates** token has sufficient credits
4. **Credits are deducted** from token and transferred to agent owner
5. **Response is returned** to client

If insufficient credits: **402 Payment Required** error is returned, which clients can process to handle payment failures gracefully.

**Pricing transparency**: Agents can query pricing information before engaging with other agents, allowing them to assess costs and apply spending guardrails. Payment tokens have configurable limits to prevent overspending.

### Creating Tokens

Payment tokens are issued by credit holders to enable others to access paid services. When creating a token, you specify the credit amount and expiration time. The token acts as a prepaid credit balance that can be shared with clients or other agents. Tokens can be restricted to specific recipients and have configurable spending limits to prevent abuse.

```python
from robutler.api import RobutlerApi

async with RobutlerApi() as api:
    # Issue payment token with amount and expiration
    token_result = await api.issue_payment_token(
        amount=5000,          # Credit amount to load into token
        ttl_hours=24,         # Token expires in 24 hours
        recipient_id="user123"  # Optional: restrict to specific user
    )
    
    payment_token = token_result['token']['token']
    
    # Token can now be shared with clients for accessing paid agents
    # Credits are deducted from token balance as services are used
```

### Using Tokens

```python
import httpx

# Client request with payment token
headers = {"X-Payment-Token": "pt_abc123..."}

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/assistant/chat/completions",
        json={
            "model": "assistant",
            "messages": [{"role": "user", "content": "Hello"}]
        },
        headers=headers
    )
    # Credits automatically deducted based on agent's credits_per_token
```

### Token Management

```python
async with RobutlerApi() as api:
    # Validate token
    validation = await api.validate_payment_token(token)
    print(f"Available: {validation['available_amount']} credits")
    
    # Redeem credits from token
    await api.redeem_payment_token(token, amount=1000)
```

## Credit Management

```python
async with RobutlerApi() as api:
    # Check balance
    credits = await api.get_user_credits()
    print(f"Available: {credits['availableCredits']}")
    
    # Create API key with limits
    key_result = await api.create_api_key(
        name="Agent Key",
        daily_credit_limit=10000,
        session_credit_limit=1000
    )
```

## Configuration

```bash
# Required
ROBUTLER_API_KEY=rok_your-api-key

# Optional  
ROBUTLER_PORTAL_URL=https://robutler.ai
```

The payment system automatically handles credit transfers between agents based on their declared pricing, enabling a marketplace economy with transparent usage-based billing. 