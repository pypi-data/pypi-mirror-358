"""
Enhanced Pricing Decorator Example

This example demonstrates the new pricing decorator that supports:
1. Fixed pricing with credits_per_call
2. Dynamic pricing with return value tuples
3. Automatic usage tracking via context
"""

import asyncio
from robutler.server import ServerBase, pricing, Pricing, get_context


class PricingExampleServer(ServerBase):
    """Example server demonstrating pricing decorator usage."""
    
    def __init__(self):
        super().__init__()
        self.setup_routes()
    
    def setup_routes(self):
        """Set up example routes."""
        
        @self.agent("fixed_pricing")
        @pricing(credits_per_call=1000, reason="Fixed price weather lookup")
        async def fixed_pricing_agent(messages, stream=False):
            """Agent with fixed pricing - always costs 1000 credits."""
            return f"Weather data for your location (fixed cost: 1000 credits)"
        
        @self.agent("dynamic_pricing") 
        @pricing()  # No fixed pricing, uses return value
        async def dynamic_pricing_agent(messages, stream=False):
            """Agent with dynamic pricing based on processing complexity."""
            # Simulate different processing complexity
            message_length = sum(len(msg.get('content', '')) for msg in messages)
            
            if message_length > 100:
                # High complexity processing
                result = f"Complex analysis of {message_length} characters"
                pricing_info = Pricing(
                    credits=message_length * 10,
                    reason=f"Complex processing of {message_length} characters",
                    metadata={
                        "processing_type": "complex",
                        "character_count": message_length,
                        "rate_per_char": 10
                    }
                )
                return result, pricing_info
            else:
                # Simple processing
                result = f"Simple analysis of {message_length} characters"
                pricing_info = Pricing(
                    credits=500,
                    reason="Simple processing",
                    metadata={
                        "processing_type": "simple",
                        "character_count": message_length
                    }
                )
                return result, pricing_info
        
        @self.agent("mixed_pricing")
        @pricing(credits_per_call=300, reason="Base processing cost")
        async def mixed_pricing_agent(messages, stream=False):
            """Agent with base cost that can override with custom pricing."""
            user_message = messages[-1].get('content', '') if messages else ''
            
            # Check if premium processing is needed
            if 'premium' in user_message.lower():
                # Override with premium pricing
                result = f"Premium processing applied to: {user_message}"
                pricing_info = Pricing(
                    credits=2000,
                    reason="Premium processing with advanced features",
                    metadata={
                        "service_tier": "premium",
                        "base_cost": 300,
                        "premium_surcharge": 1700
                    }
                )
                return result, pricing_info
            
            # Use base pricing (300 credits from decorator)
            return f"Standard processing: {user_message}"


# Example usage functions
@pricing(credits_per_call=100)
def simple_tool(data: str) -> str:
    """Simple tool with fixed pricing."""
    return f"Processed: {data}"


@pricing()
def variable_tool(data: str) -> tuple:
    """Tool with variable pricing based on data size."""
    processing_cost = len(data) * 5
    result = f"Variable processing of {len(data)} characters"
    
    pricing_info = Pricing(
        credits=processing_cost,
        reason=f"Variable processing: {len(data)} chars × 5 credits/char",
        metadata={
            "data_length": len(data),
            "rate_per_char": 5,
            "total_cost": processing_cost
        }
    )
    
    return result, pricing_info


@pricing(credits_per_call=500)
def conditional_tool(data: str, premium: bool = False):
    """Tool that can override base pricing conditionally."""
    if premium:
        # Override with premium pricing
        result = f"Premium processing: {data}"
        pricing_info = Pricing(
            credits=1500,
            reason="Premium processing requested",
            metadata={
                "service_level": "premium",
                "base_cost": 500,
                "premium_upgrade": 1000
            }
        )
        return result, pricing_info
    
    # Use base pricing (500 credits)
    return f"Standard processing: {data}"


async def example_usage():
    """Demonstrate the pricing decorator in action."""
    print("=== Pricing Decorator Example ===\n")
    
    # Test tools directly (outside of server context)
    print("1. Direct tool usage (no context):")
    result1 = simple_tool("test data")
    print(f"   Result: {result1}")
    
    result2, pricing2 = variable_tool("this is longer data")
    print(f"   Result: {result2}")
    print(f"   Pricing: {pricing2}")
    
    result3 = conditional_tool("data", premium=False)
    print(f"   Result: {result3}")
    
    result4, pricing4 = conditional_tool("data", premium=True)
    print(f"   Result: {result4}")
    print(f"   Pricing: {pricing4}")
    
    print("\n2. Usage tracking example:")
    print("   (In a real server context, usage would be automatically tracked)")
    print("   - simple_tool: 100 credits")
    print("   - variable_tool: 95 credits (19 chars × 5)")
    print("   - conditional_tool (standard): 500 credits")
    print("   - conditional_tool (premium): 1500 credits")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())
    
    print("\n=== Server Example ===")
    print("To run the server with these pricing examples:")
    print("1. Create a PricingExampleServer instance")
    print("2. Make requests to /fixed_pricing/chat/completions")
    print("3. Make requests to /dynamic_pricing/chat/completions") 
    print("4. Make requests to /mixed_pricing/chat/completions")
    print("5. Check usage reports in finalize_request callbacks") 