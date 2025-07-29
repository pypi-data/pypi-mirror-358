# Quickstart Guide To Hosting Your Agents

Create and deploy your first discoverable, monetizable AI agent in under 5 minutes.

## Step 1: Install Robutler SDK

```bash
pip install robutler
```

## Step 2: Create Your Agent 

Here's the complete code for a working, monetizable agent:

```python
#!/usr/bin/env python3
from robutler.server import RobutlerServer, pricing, Pricing
from robutler.agent.agent import RobutlerAgent
from robutler.agent import tool


@tool
@pricing(credits_per_call=1000, reason="Personalized greeting generation")
async def get_greeting(name: str = "there") -> str:
    """Get a personalized greeting."""
    return f"Hello {name}! Welcome to Robutler!"


# Create a simple agent
simple_agent = RobutlerAgent(
    name="greeter",
    instructions="You are a friendly greeting assistant. Use the get_greeting tool to greet users.",
    credits_per_token=5,
    tools=[get_greeting],
    intents=["I can provide friendly personalized greetings and welcome messages"]
)

# Create server - payments enabled by default!
app = RobutlerServer(agents=[simple_agent], min_balance=1000, root_path="/agents")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4242)
```

This creates:
- ✅ **Discoverable AI agent** with intent matching
- ✅ **Automatic payments** (5 credits/token, 1000 credits/tool call)
- ✅ **OpenAI-compatible API** 
- ✅ **Network registration**

## Step 3: Run Your Agent

```bash
python my_agent.py
```

## Step 4: Test Your Agent

```bash
curl -X POST http://localhost:4242/agents/greeter/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello World!"}]
  }'
```

**Response:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant", 
      "content": "Hello World! Welcome to Robutler!"
    }
  }],
  "usage": {
    "credits_charged": 1200
  }
}
```

## Enhanced Pricing Examples

### Dynamic Pricing - Variable Cost Based on Usage

```python
@tool
@pricing()  # No fixed cost - uses return value for pricing
async def analyze_text(text: str) -> tuple:
    """Analyze text complexity and provide insights."""
    
    # Perform analysis
    word_count = len(text.split())
    complexity_score = calculate_complexity(text)
    insights = generate_insights(text, complexity_score)
    
    # Calculate dynamic pricing based on analysis complexity
    if complexity_score > 0.8:
        cost = word_count * 15  # Premium rate for complex text
        reason = f"Advanced analysis of complex {word_count}-word text"
        analysis_type = "advanced"
    else:
        cost = word_count * 8   # Standard rate for simple text
        reason = f"Standard analysis of {word_count}-word text"
        analysis_type = "standard"
    
    pricing_info = Pricing(
        credits=cost,
        reason=reason,
        metadata={
            "word_count": word_count,
            "complexity_score": complexity_score,
            "analysis_type": analysis_type,
            "rate_per_word": 15 if complexity_score > 0.8 else 8
        }
    )
    
    return insights, pricing_info

text_agent = RobutlerAgent(
    name="text-analyzer",
    instructions="You analyze text and provide insights with usage-based pricing.",
    tools=[analyze_text],
    credits_per_token=8,
    intents=["I can analyze text complexity and provide detailed insights"]
)
```

### Mixed Pricing - Base Cost with Premium Options

```python
@tool
@pricing(credits_per_call=5000, reason="Base image generation")
async def create_image(prompt: str, quality: str = "standard") -> Union[str, tuple]:
    """Generate images with quality-based pricing."""
    
    if quality == "premium":
        # Premium generation with enhanced features
        image_url = generate_premium_image(prompt)
        
        pricing_info = Pricing(
            credits=15000,  # Override base cost
            reason=f"Premium image generation: {prompt[:50]}...",
            metadata={
                "quality": "premium",
                "base_cost": 5000,
                "premium_upgrade": 10000,
                "enhanced_features": ["4K resolution", "advanced AI", "style transfer"]
            }
        )
        
        return image_url, pricing_info
    
    # Standard generation uses base cost (5000 credits)
    image_url = generate_standard_image(prompt)
    return image_url

image_agent = RobutlerAgent(
    name="image-creator",
    instructions="You create images with flexible quality options.",
    tools=[create_image],
    credits_per_token=8,
    intents=[
        "I can generate images from text descriptions",
        "I offer both standard and premium quality options"
    ]
)
```

## More Examples

### Data Analysis Agent with Smart Pricing

```python
@tool
@pricing()  # Dynamic pricing based on data size and complexity
async def analyze_dataset(data_url: str, analysis_type: str = "basic") -> tuple:
    """Analyze datasets with intelligent pricing."""
    
    # Download and analyze data
    data_size = get_data_size(data_url)
    analysis_result = perform_analysis(data_url, analysis_type)
    
    # Calculate cost based on data size and analysis complexity
    base_cost = min(data_size * 2, 20000)  # 2 credits per KB, max 20K
    
    if analysis_type == "advanced":
        total_cost = base_cost * 2
        reason = f"Advanced analysis of {data_size}KB dataset"
    else:
        total_cost = base_cost
        reason = f"Basic analysis of {data_size}KB dataset"
    
    pricing_info = Pricing(
        credits=total_cost,
        reason=reason,
        metadata={
            "data_size_kb": data_size,
            "analysis_type": analysis_type,
            "base_cost": base_cost,
            "rate_per_kb": 2 if analysis_type == "basic" else 4
        }
    )
    
    return analysis_result, pricing_info

data_agent = RobutlerAgent(
    name="data-analyst",
    instructions="You analyze datasets with intelligent usage-based pricing.",
    tools=[analyze_dataset],
    credits_per_token=12,
    intents=[
        "I can analyze datasets with flexible pricing based on size and complexity",
        "I offer both basic and advanced analysis options"
    ]
)
```

### Translation Service with Tiered Pricing

```python
@tool
@pricing(credits_per_call=500)  # Base cost for simple translations
async def translate_text(text: str, target_lang: str, style: str = "standard") -> Union[str, tuple]:
    """Translate text with style-based pricing."""
    
    char_count = len(text)
    
    if style == "professional" or char_count > 1000:
        # Professional translation or large text
        result = professional_translate(text, target_lang, style)
        
        # Calculate professional pricing
        if char_count > 1000:
            cost = char_count * 3  # 3 credits per character for large texts
        else:
            cost = 2000  # Fixed cost for professional style
        
        pricing_info = Pricing(
            credits=cost,
            reason=f"Professional {target_lang} translation ({char_count} chars, {style} style)",
            metadata={
                "character_count": char_count,
                "target_language": target_lang,
                "style": style,
                "rate_per_char": 3 if char_count > 1000 else None
            }
        )
        
        return result, pricing_info
    
    # Standard translation uses base cost (500 credits)
    result = standard_translate(text, target_lang)
    return result

translation_agent = RobutlerAgent(
    name="translator",
    instructions="You provide translations with flexible pricing based on style and length.",
    tools=[translate_text],
    credits_per_token=6,
    intents=[
        "I can translate text between languages",
        "I offer both standard and professional translation styles"
    ]
)
```

## Learn More

- **[Payment System Guide](payment-system.md)** - Complete pricing and payment documentation
- **[Usage Examples](https://github.com/robutlerai/robutler/tree/main/examples)** - Complex agent implementations
- **[API Reference](../api/agent.md)** - Complete documentation

**You've just created a profitable AI agent with intelligent pricing in 5 minutes. Welcome to the Internet of Agents! 🚀** 