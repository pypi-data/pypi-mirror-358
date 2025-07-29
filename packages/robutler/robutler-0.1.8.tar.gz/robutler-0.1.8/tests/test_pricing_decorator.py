"""
Tests for the enhanced pricing decorator
"""

import pytest
from unittest.mock import Mock, patch
from robutler.server import pricing, Pricing, get_context


class TestPricingDecorator:
    """Test the enhanced pricing decorator functionality."""
    
    def test_pricing_import(self):
        """Test that pricing decorator and Pricing model can be imported."""
        assert callable(pricing)
        assert Pricing is not None
    
    def test_fixed_pricing_decorator(self):
        """Test decorator with fixed credits_per_call."""
        @pricing(credits_per_call=100)
        def test_func(data):
            return f"Processed: {data}"
        
        # Function should work normally
        result = test_func("test")
        assert result == "Processed: test"
    
    def test_dynamic_pricing_decorator(self):
        """Test decorator with dynamic pricing via return value."""
        @pricing()
        def test_func(data):
            cost = len(data) * 5
            pricing_info = Pricing(
                credits=cost,
                reason=f"Processing {len(data)} characters",
                metadata={"length": len(data)}
            )
            return f"Result: {data}", pricing_info
        
        # Function should return both result and pricing
        result, pricing_info = test_func("hello")
        assert result == "Result: hello"
        assert isinstance(pricing_info, Pricing)
        assert pricing_info.credits == 25  # 5 chars * 5 credits
        assert "5 characters" in pricing_info.reason
        assert pricing_info.metadata["length"] == 5
    
    def test_mixed_pricing_decorator(self):
        """Test decorator that can use both fixed and dynamic pricing."""
        @pricing(credits_per_call=50)
        def test_func(data, premium=False):
            if premium:
                pricing_info = Pricing(
                    credits=200,
                    reason="Premium processing",
                    metadata={"premium": True}
                )
                return f"Premium: {data}", pricing_info
            return f"Standard: {data}"
        
        # Standard usage should return simple result
        result1 = test_func("test")
        assert result1 == "Standard: test"
        
        # Premium usage should return tuple with pricing
        result2, pricing_info = test_func("test", premium=True)
        assert result2 == "Premium: test"
        assert pricing_info.credits == 200
        assert pricing_info.metadata["premium"] is True
    
    def test_pricing_model_validation(self):
        """Test Pricing model validation."""
        # Valid pricing object
        pricing_info = Pricing(
            credits=100,
            reason="Test processing",
            metadata={"test": True}
        )
        assert pricing_info.credits == 100
        assert pricing_info.reason == "Test processing"
        assert pricing_info.metadata["test"] is True
        
        # Test with empty metadata (should default to {})
        pricing_info2 = Pricing(credits=50, reason="Simple test")
        assert pricing_info2.metadata == {}
    
    def test_async_function_support(self):
        """Test that decorator works with async functions."""
        @pricing(credits_per_call=75)
        async def async_test_func(data):
            return f"Async processed: {data}"
        
        import asyncio
        
        async def run_test():
            result = await async_test_func("test")
            return result
        
        result = asyncio.run(run_test())
        assert result == "Async processed: test"
    
    def test_custom_reason(self):
        """Test decorator with custom reason parameter."""
        @pricing(credits_per_call=100, reason="Custom API call")
        def test_func(data):
            return f"Processed: {data}"
        
        # Function should work (usage tracking tested separately)
        result = test_func("test")
        assert result == "Processed: test"
    
    def test_no_context_graceful_handling(self):
        """Test that decorator works gracefully when no context is available."""
        @pricing(credits_per_call=100)
        def test_func(data):
            return f"Processed: {data}"
        
        # Should work without context (no tracking)
        result = test_func("test")
        assert result == "Processed: test"
    
    @patch('robutler.server.base.get_context')
    def test_usage_tracking_fixed_pricing(self, mock_get_context):
        """Test usage tracking with fixed pricing."""
        mock_context = Mock()
        mock_get_context.return_value = mock_context
        
        @pricing(credits_per_call=100, reason="Test API call")
        def test_func(data):
            return f"Processed: {data}"
        
        result = test_func("test")
        
        # Verify context.track_usage was called
        mock_context.track_usage.assert_called_once_with(
            credits=100,
            reason="Test API call",
            metadata={"function": "test_func", "pricing_type": "fixed"}
        )
        assert result == "Processed: test"
    
    @patch('robutler.server.base.get_context')
    def test_usage_tracking_dynamic_pricing(self, mock_get_context):
        """Test usage tracking with dynamic pricing."""
        mock_context = Mock()
        mock_get_context.return_value = mock_context
        
        @pricing()
        def test_func(data):
            pricing_info = Pricing(
                credits=150,
                reason="Dynamic processing",
                metadata={"complexity": "high"}
            )
            return f"Result: {data}", pricing_info
        
        result = test_func("test")
        
        # Verify context.track_usage was called with dynamic pricing
        mock_context.track_usage.assert_called_once_with(
            credits=150,
            reason="Dynamic processing",
            metadata={"complexity": "high"}
        )
        assert result == "Result: test"
    
    @patch('robutler.server.base.get_context')
    def test_default_reason_generation(self, mock_get_context):
        """Test that default reason is generated from function name."""
        mock_context = Mock()
        mock_get_context.return_value = mock_context
        
        @pricing(credits_per_call=100)
        def my_special_function(data):
            return f"Processed: {data}"
        
        result = my_special_function("test")
        
        # Verify default reason was generated
        mock_context.track_usage.assert_called_once_with(
            credits=100,
            reason="Function 'my_special_function' called",
            metadata={"function": "my_special_function", "pricing_type": "fixed"}
        )
    
    def test_function_metadata_preservation(self):
        """Test that decorator preserves function metadata."""
        @pricing(credits_per_call=100)
        def documented_function(data: str) -> str:
            """This function has documentation."""
            return f"Processed: {data}"
        
        # Metadata should be preserved
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This function has documentation."
        
        # Function should still work
        result = documented_function("test")
        assert result == "Processed: test"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"]) 