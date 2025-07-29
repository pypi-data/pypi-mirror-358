#!/usr/bin/env python3
"""
Natural Language Interface (NLI) Tool

This tool communicates with RobutlerAgent servers, handles payment tokens automatically,
and provides seamless integration with MCP servers.
"""

import os
import json
import asyncio
import httpx
import logging
from typing import Optional, Dict, Any, List
from robutler.api import initialize_api, RobutlerApiError

# Try to import get_context for token reuse
try:
    from fastmcp.server.dependencies import get_context
except ImportError:
    try:
        from robutler.server.base import get_context
    except ImportError:
        get_context = None

# Configure logging
logger = logging.getLogger(__name__)


class NLIClient:
    """Client for communicating with agents discovered with robutler_discovery."""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the NLI client.
        
        Args:
            api_token: Robutler API token (defaults to ROBUTLER_API_KEY env var)
        """
        self.api_token = api_token or os.getenv('ROBUTLER_API_KEY')
        self.api_client = None
        self.payment_tokens: Dict[str, str] = {}  # Cache payment tokens per server
        
    async def _ensure_api_client(self):
        """Ensure the API client is initialized."""
        if self.api_client is None:
            if not self.api_token:
                raise ValueError("Robutler API token not provided. Set ROBUTLER_API_KEY environment variable.")
            
            # Set the API key in settings for initialize_api
            from robutler.settings import settings
            original_api_key = settings.api_key
            settings.api_key = self.api_token
            
            try:
                self.api_client = await initialize_api()
                logger.info("NLI API client initialized successfully")
            except Exception as e:
                settings.api_key = original_api_key  # Restore original
                raise ValueError(f"Failed to initialize Robutler API client: {e}")
    
    async def _get_payment_token(self, server_url: str, min_balance: str = "10000") -> str:
        """
        Get or create a payment token for the specified server.
        
        Args:
            server_url: The RobutlerAgent server URL
            min_balance: Minimum balance required for the token
            
        Returns:
            Payment token string
        """
        await self._ensure_api_client()
        
        # Check if we have a cached token for this server
        if server_url in self.payment_tokens:
            token = self.payment_tokens[server_url]
            try:
                # Validate the cached token
                validation = await self.api_client.validate_payment_token(token)
                if validation.get('valid', False):
                    token_info = validation.get('token', {})
                    available = token_info.get('availableAmount', 0)
                    if available >= min_balance:
                        return token
                    else:
                        logger.warning(f"Cached token has insufficient balance: {available} < {min_balance}")
                else:
                    logger.warning("Cached token is invalid")
            except Exception as e:
                logger.warning(f"Error validating cached token: {e}")
            
            # Remove invalid/insufficient token from cache
            del self.payment_tokens[server_url]
        
        # Create a new payment token
        logger.info(f"Creating new payment token for {server_url}")
        try:
            # Create token with 2x the minimum balance to avoid frequent renewals
            # Convert to decimal for precise arithmetic
            min_balance_decimal = float(min_balance)
            token_amount = str(max(min_balance_decimal * 2, 50000))
            result = await self.api_client.issue_payment_token(
                amount=token_amount,
                ttl_hours=24  # Valid for 24 hours
            )
            
            token_info = result.get('token', {})
            token_string = token_info.get('token', '')
            
            if not token_string:
                raise ValueError("Failed to create payment token")
            
            # Cache the token
            self.payment_tokens[server_url] = token_string
            
            logger.info(f"Created payment token with {token_info.get('amount', 0)} credits")
            return token_string
            
        except Exception as e:
            raise ValueError(f"Failed to create payment token: {e}")
    
    def _get_tokens_from_context(self):
        """
        Get tokens from the current request context.
        
        Returns:
            tuple: (payment_token, origin_token, peer_identity_token)
        """
        payment_token = None
        origin_token = None
        peer_identity_token = None
        
        if get_context:
            try:
                ctx = get_context()
                if ctx:
                    # Get payment token from context
                    payment_token = ctx.get('payment_token')
                    
                    # Get origin token from context
                    origin_token = ctx.get('origin_token')
                    
                    # Get peer identity token from context
                    peer_identity_token = ctx.get('peer_identity_token')
                    
                    logger.debug(f"Context tokens - payment: {'✓' if payment_token else '✗'}, "
                               f"origin: {'✓' if origin_token else '✗'}, "
                               f"peer: {'✓' if peer_identity_token else '✗'}")
            except Exception as e:
                logger.debug(f"Could not get context: {e}")
        
        return payment_token, origin_token, peer_identity_token
    
    async def chat_completion(
        self, 
        agent_url: str, 
        messages: List[Dict[str, str]], 
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to a RobutlerAgent server.
        
        Args:
            agent_url: URL of the RobutlerAgent server endpoint
            messages: List of chat messages
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Response from the agent server
        """
        # Ensure URL ends with /chat/completions
        if not agent_url.endswith('/chat/completions'):
            if agent_url.endswith('/'):
                agent_url = agent_url + 'chat/completions'
            else:
                agent_url = agent_url + '/chat/completions'
        
        # Extract agent name from URL for model parameter
        # URL format: http://host:port/path/agent_name/chat/completions
        url_parts = agent_url.rstrip('/').split('/')
        # Remove 'chat' and 'completions' from the end to get agent name
        if len(url_parts) >= 3 and url_parts[-1] == 'completions' and url_parts[-2] == 'chat':
            agent_name = url_parts[-3]
        elif len(url_parts) >= 2:
            agent_name = url_parts[-2]
        else:
            agent_name = "gpt-4o-mini"
        
        # Prepare request data
        request_data = {
            "model": agent_name,  # Use agent name as model
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Get tokens from context
        context_payment_token, context_origin_token, context_peer_token = self._get_tokens_from_context()
        
        # Token logic implementation:
        # 1. If there is a payment token in the context, reuse it
        # 2. If there is an origin token in the context, reuse it
        # 3. Set the peer token to the generated payment token
        
        payment_token_to_use = None
        origin_token_to_use = None
        peer_token_to_use = None
        generated_payment_token = None
        
        # Step 1: Handle payment token
        if context_payment_token:
            payment_token_to_use = context_payment_token
            logger.debug("Reusing payment token from context")
        
        # Step 2: Handle origin token
        if context_origin_token:
            origin_token_to_use = context_origin_token
            logger.debug("Reusing origin token from context")
        
        # Add tokens to headers if available
        if payment_token_to_use:
            headers["X-Payment-Token"] = payment_token_to_use
        
        if origin_token_to_use:
            headers["X-Origin-Token"] = origin_token_to_use
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First attempt with available tokens
            try:
                response = await client.post(agent_url, json=request_data, headers=headers)
                
                if response.status_code == 200:
                    # Success - set peer token if we have payment token
                    if payment_token_to_use or generated_payment_token:
                        peer_token_to_use = payment_token_to_use or generated_payment_token
                        if peer_token_to_use:
                            # Add peer identity token header for successful request
                            # Note: This would typically be handled by the calling context
                            logger.debug(f"Would set peer identity token: {peer_token_to_use[:10]}...")
                    
                    if stream:
                        return {"status": "success", "content": response.text}
                    else:
                        return response.json()
                
                elif response.status_code == 402:
                    # Payment required - extract minimum balance from error message
                    error_text = response.text
                    min_balance = 10000  # Default
                    
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', '')
                        
                        # Try to extract minimum balance from error message
                        if 'Required:' in error_detail:
                            # Format: "Insufficient token balance. Available: X, Required: Y"
                            parts = error_detail.split('Required:')
                            if len(parts) > 1:
                                min_balance = int(parts[1].strip().split()[0])
                        elif 'minimum balance' in error_detail.lower():
                            # Try to extract number from error message
                            import re
                            numbers = re.findall(r'\d+', error_detail)
                            if numbers:
                                min_balance = int(numbers[-1])  # Take the last number
                    except Exception as e:
                        logger.warning(f"Could not parse payment error details: {e}")
                        pass  # Use default min_balance
                    
                    logger.info(f"💳 Payment required for {agent_url} (min balance: {min_balance} credits), obtaining payment token")
                    
                    # Generate a new payment token if we don't have one or if the existing one failed
                    try:
                        generated_payment_token = await self._get_payment_token(agent_url, min_balance)
                        
                        # Use the generated payment token
                        headers["X-Payment-Token"] = generated_payment_token
                        
                        # Set peer token to the generated payment token
                        peer_token_to_use = generated_payment_token
                        if peer_token_to_use:
                            headers["X-Peer-Identity"] = peer_token_to_use
                        
                        logger.info(f"🔄 Retrying request with generated payment token and peer identity token")
                        
                        # Retry with payment token and peer identity token
                        response = await client.post(agent_url, json=request_data, headers=headers)
                        
                        if response.status_code == 200:
                            logger.info(f"✅ Request successful with generated tokens")
                            if stream:
                                return {"status": "success", "content": response.text}
                            else:
                                return response.json()
                        else:
                            logger.error(f"❌ Request failed even with generated tokens: {response.status_code}")
                            raise ValueError(f"Request failed even with generated tokens: {response.status_code} - {response.text}")
                    except Exception as e:
                        logger.error(f"❌ Token generation and handling failed: {e}")
                        raise ValueError(f"Token generation and handling failed: {e}")
                
                else:
                    raise ValueError(f"Request failed: {response.status_code} - {response.text}")
                    
            except httpx.RequestError as e:
                raise ValueError(f"Network error communicating with {agent_url}: {e}")
    
    async def get_agent_info(self, agent_url: str) -> Dict[str, Any]:
        """
        Get information about a RobutlerAgent.
        
        Args:
            agent_url: Base URL of the RobutlerAgent server
            
        Returns:
            Agent information
        """
        # Remove /chat/completions if present
        if agent_url.endswith('/chat/completions'):
            agent_url = agent_url[:-len('/chat/completions')]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(agent_url)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise ValueError(f"Failed to get agent info: {response.status_code} - {response.text}")
            except httpx.RequestError as e:
                raise ValueError(f"Network error getting agent info from {agent_url}: {e}")
    
    async def close(self):
        """Close the API client."""
        if self.api_client:
            await self.api_client.close()


# Main NLI function for MCP integration
async def robutler_nli(agent_url: str, message: str) -> str:
    """
    Natural Language Interface to communicate with RobutlerAgent servers.
    
    Args:
        agent_url: URL of the RobutlerAgent server (e.g., http://localhost:2226/api/assistant)
        message: Message to send to the agent
        
    Returns:
        Response from the agent
    """
    client = NLIClient()
    
    try:
        messages = [{"role": "user", "content": message}]
        
        result = await client.chat_completion(
            agent_url=agent_url,
            messages=messages,
            stream=False
        )
        
        choices = result.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "No response")
        else:
            return "No response from agent"
                
    except Exception as e:
        return f"Error communicating with agent: {e}"
    finally:
        await client.close()


# CLI Interface for testing
async def main():
    """CLI interface for testing the NLI tool."""
    import sys
    
    if len(sys.argv) < 3:
        logger.info("Usage: python nli.py <agent_url> <message>")
        logger.info("Example: python nli.py http://localhost:2226/api/assistant 'What time is it?'")
        return
    
    agent_url = sys.argv[1]
    message = sys.argv[2]
    
    logger.info(f"🤖 Sending message to {agent_url}")
    logger.info(f"💬 Message: {message}")
    logger.info("")
    
    # Send chat message
    logger.info("💬 Sending chat message...")
    response = await robutler_nli(agent_url, message)
    logger.info(f"🤖 Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
