#!/usr/bin/env python3
"""
Test NLI token logic implementation
"""
import asyncio
import logging
from unittest.mock import Mock, patch, AsyncMock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_token_context_extraction():
    """Test token extraction from context"""
    
    logger.info("Testing token extraction from context...")
    
    # Import the NLIClient
    from robutler.tools.nli import NLIClient
    
    # Create NLI client
    client = NLIClient()
    
    # Test 1: All tokens available in context
    mock_context = Mock()
    mock_context.get.side_effect = lambda key: {
        'payment_token': 'payment_token_123',
        'origin_token': 'origin_token_456', 
        'peer_identity_token': 'peer_token_789'
    }.get(key)
    
    with patch('robutler.tools.nli.get_context', return_value=mock_context):
        payment, origin, peer = client._get_tokens_from_context()
        
        assert payment == 'payment_token_123', f"Expected payment_token_123, got {payment}"
        assert origin == 'origin_token_456', f"Expected origin_token_456, got {origin}"
        assert peer == 'peer_token_789', f"Expected peer_token_789, got {peer}"
        
        logger.info("✅ All tokens extracted correctly from context")
    
    # Test 2: Only payment token available
    mock_context2 = Mock()
    mock_context2.get.side_effect = lambda key: {
        'payment_token': 'payment_only_123'
    }.get(key)
    
    with patch('robutler.tools.nli.get_context', return_value=mock_context2):
        payment, origin, peer = client._get_tokens_from_context()
        
        assert payment == 'payment_only_123', f"Expected payment_only_123, got {payment}"
        assert origin is None, f"Expected None for origin, got {origin}"
        assert peer is None, f"Expected None for peer, got {peer}"
        
        logger.info("✅ Payment token only extracted correctly")
    
    # Test 3: No context available
    with patch('robutler.tools.nli.get_context', return_value=None):
        payment, origin, peer = client._get_tokens_from_context()
        
        assert payment is None, f"Expected None for payment, got {payment}"
        assert origin is None, f"Expected None for origin, got {origin}"
        assert peer is None, f"Expected None for peer, got {peer}"
        
        logger.info("✅ No context handled correctly")
    
    logger.info("🎉 Token context extraction tests passed!")

async def test_token_header_logic():
    """Test token header logic in chat completion"""
    
    logger.info("Testing token header logic...")
    
    from robutler.tools.nli import NLIClient
    
    client = NLIClient()
    
    # Mock the get_context to return specific tokens
    mock_context = Mock()
    mock_context.get.side_effect = lambda key: {
        'payment_token': 'context_payment_123',
        'origin_token': 'context_origin_456'
    }.get(key)
    
    # Mock the HTTP client to capture headers
    captured_headers = {}
    
    async def mock_post(url, json=None, headers=None):
        captured_headers.update(headers or {})
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        return mock_response
    
    with patch('robutler.tools.nli.get_context', return_value=mock_context):
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = mock_post
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Test chat completion
            try:
                result = await client.chat_completion(
                    agent_url="http://test.com/agent",
                    messages=[{"role": "user", "content": "test"}]
                )
                
                # Verify headers were set correctly
                assert "X-Payment-Token" in captured_headers, "Payment token header not set"
                assert captured_headers["X-Payment-Token"] == "context_payment_123", f"Wrong payment token: {captured_headers.get('X-Payment-Token')}"
                
                assert "X-Origin-Token" in captured_headers, "Origin token header not set"
                assert captured_headers["X-Origin-Token"] == "context_origin_456", f"Wrong origin token: {captured_headers.get('X-Origin-Token')}"
                
                logger.info("✅ Token headers set correctly from context")
                logger.info(f"Headers: {captured_headers}")
                
            except Exception as e:
                logger.error(f"❌ Test failed: {e}")
                raise

async def test_payment_token_generation():
    """Test payment token generation and peer token setting"""
    
    logger.info("Testing payment token generation and peer token setting...")
    
    from robutler.tools.nli import NLIClient
    
    client = NLIClient()
    
    # Mock no tokens in context initially
    mock_context = Mock()
    mock_context.get.return_value = None
    
    # Mock payment required response, then successful response
    call_count = 0
    captured_headers_list = []
    
    async def mock_post(url, json=None, headers=None):
        nonlocal call_count
        captured_headers_list.append(headers.copy() if headers else {})
        call_count += 1
        
        if call_count == 1:
            # First call - payment required
            mock_response = Mock()
            mock_response.status_code = 402
            mock_response.text = "Payment required. Minimum balance: 5000 credits"
            mock_response.json.return_value = {
                "detail": "Payment required. Minimum balance: 5000 credits"
            }
            return mock_response
        else:
            # Second call - success with tokens
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Success with tokens"}}]
            }
            return mock_response
    
    # Mock the payment token generation
    with patch('robutler.tools.nli.get_context', return_value=mock_context):
        with patch.object(client, '_get_payment_token', return_value='generated_payment_token_123') as mock_get_token:
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client.post = mock_post
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                try:
                    result = await client.chat_completion(
                        agent_url="http://test.com/agent",
                        messages=[{"role": "user", "content": "test"}]
                    )
                    
                    # Verify payment token was generated
                    mock_get_token.assert_called_once()
                    
                    # Verify first call had no payment token
                    first_headers = captured_headers_list[0]
                    assert "X-Payment-Token" not in first_headers, f"Unexpected payment token in first call: {first_headers}"
                    
                    # Verify second call had both payment and peer tokens
                    second_headers = captured_headers_list[1]
                    assert "X-Payment-Token" in second_headers, "Payment token missing in second call"
                    assert second_headers["X-Payment-Token"] == "generated_payment_token_123", f"Wrong payment token: {second_headers.get('X-Payment-Token')}"
                    
                    assert "X-Peer-Identity" in second_headers, "Peer identity token missing in second call"
                    assert second_headers["X-Peer-Identity"] == "generated_payment_token_123", f"Wrong peer token: {second_headers.get('X-Peer-Identity')}"
                    
                    logger.info("✅ Payment token generation and peer token setting works correctly")
                    logger.info(f"First call headers: {first_headers}")
                    logger.info(f"Second call headers: {second_headers}")
                    
                except Exception as e:
                    logger.error(f"❌ Test failed: {e}")
                    raise

async def main():
    """Run all tests"""
    logger.info("🧪 Starting NLI token logic tests...")
    
    try:
        test_token_context_extraction()
        await test_token_header_logic()
        await test_payment_token_generation()
        
        logger.info("🎉 All NLI token logic tests passed!")
        
    except Exception as e:
        logger.error(f"💥 Tests failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 