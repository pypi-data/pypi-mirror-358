"""
Robutler Server - Enhanced ServerBase with agent management

This module provides the main Server class that extends ServerBase with basic
agent management functionality.

Key Features:
    * Automatic agent registration and endpoint creation
    * Agent lifecycle management
    * Pricing decorator for cost tracking
    * Usage tracking for finalize callbacks

Example Usage:
    Basic server with agents:
    
    ```python
    from robutler.server import Server
    
    # Create server with agents
    app = Server(agents=[agent1, agent2])
    ```
    
    Using the pricing decorator:
    
    ```python
    from robutler.server import pricing
    
    @pricing(credits_per_call=1000)
    async def my_agent(messages, stream=False):
        return "Response"
    ```
"""

from typing import List, Optional, Callable, Any
from functools import wraps
import os
import logging
import asyncio

# Set up logger
logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional - if not installed, just continue
    pass

from .base import ServerBase, _current_request, pricing, get_context
from datetime import datetime


# pricing decorator is now imported from base module


class Server(ServerBase):
    """
    Enhanced server that extends ServerBase with basic agent functionality.
    
    This class adds automatic agent registration and endpoint creation
    on top of the base server.
    """
    
    def __init__(self, agents: Optional[List] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.agents = agents or []
        
        # Register usage tracking callback
        self._register_autopay_callback()
        
        # Create agent endpoints
        if self.agents:
            self._create_agent_endpoints(self.agents)
    
    def _register_autopay_callback(self):
        """
        Register a single finalize callback that handles usage tracking for all agent types.
        """
        @self.agent.finalize_request
        async def autopay_callback(request, response):
            """
            Autopay callback for all agent types.
            Handles RobutlerAgent, dynamic portal agents, and other agent types.
            """
            # Get context and print tracked usage to logs
            try:
                context = get_context()
                if context:
                    usage_summary = context.usage
                    
                    # Log usage summary if there were any operations
                    if usage_summary['total_operations'] > 0:
                        logger.info(f"\n💰 Usage Summary - {datetime.utcnow().isoformat()}")
                        logger.info(f"   📊 Total Operations: {usage_summary['total_operations']}")
                        logger.info(f"   🪙 Total Credits: {usage_summary['total_credits']}")
                        logger.info(f"   ⏱️ Duration: {usage_summary['duration_seconds']:.3f}s")
                        
                        # Log individual operations
                        logger.info(f"   📋 Operations:")
                        for operation in usage_summary['receipt']['operations']:
                            metadata = operation.get('metadata', {})
                            model = metadata.get('model', 'unknown')
                            streaming = metadata.get('streaming', False)
                            logger.info(f"      • {operation['reason']}")
                            logger.info(f"        Credits: {operation['credits']}, Model: {model}, Streaming: {streaming}")
                            if 'input_tokens' in metadata and 'output_tokens' in metadata:
                                logger.info(f"        Tokens: {metadata['input_tokens']} input + {metadata['output_tokens']} output = {metadata.get('total_tokens', 0)} total")
                        
                        logger.info("   " + "─" * 60)
                        
                        # Charge payment token if applicable - separate by usage kind
                        total_credits = usage_summary['total_credits']
                        if total_credits > 0:
                            # Separate usage by kind
                            operations = usage_summary['receipt']['operations']
                            llm_credits = sum(op['credits'] for op in operations if op.get('kind') == 'llm_tokens')
                            other_credits = sum(op['credits'] for op in operations if op.get('kind') != 'llm_tokens')
                            
                            # Get agent's profit margin from request state
                            agent_profit_margin = 1.0  # Default to no additional margin
                            if hasattr(request, 'state') and hasattr(request.state, 'agent_state'):
                                agent_state = request.state.agent_state
                                if 'portal_data' in agent_state:
                                    portal_data = agent_state['portal_data']
                                    if portal_data and 'profitMargin' in portal_data:
                                        # Convert percentage to multiplier (e.g., 20% -> 1.20)
                                        profit_percentage = portal_data['profitMargin']
                                        agent_profit_margin = 1.0 + (profit_percentage / 100.0)
                            
                            # Add agent's profit margin on LLM credits to other_credits
                            agent_llm_margin = llm_credits * (agent_profit_margin - 1.0)
                            other_credits = other_credits + agent_llm_margin
                            
                            logger.debug(f"💳 Credits breakdown: {llm_credits} LLM tokens, {other_credits} other (includes {agent_llm_margin} agent LLM margin @ {agent_profit_margin:.2f}x)")
                            
                            # Charge LLM tokens with ROBUTLER_API_KEY
                            if llm_credits > 0:
                                await self._charge_payment_token(request, llm_credits, use_robutler_key=True)
                            
                            # Charge other usage with agent's API key
                            if other_credits > 0:
                                await self._charge_payment_token(request, other_credits, use_robutler_key=False)
                        else:
                            logger.debug("💳 No credits to charge")
                    else:
                        logger.debug("💰 No usage operations tracked for this request")
                else:
                    logger.debug("💰 No context available for usage tracking")
            except Exception as e:
                logger.error(f"⚠️ Error in usage tracker: {e}")
    
    
    
    async def _charge_payment_token(self, request, credits_to_charge, use_robutler_key=False, agent_api_key=None):
        """
        Charge the payment token for the calculated usage.
        
        Args:
            request: FastAPI request object
            credits_to_charge: Number of credits to charge
            use_robutler_key: If True, use ROBUTLER_API_KEY; if False, use agent's API key
            agent_api_key: Agent's specific API key for authentication (deprecated, use use_robutler_key)
        """
        try:
            # Get payment token from request context
            payment_token = None
            if hasattr(request, 'state') and hasattr(request.state, 'payment_token'):
                payment_token = request.state.payment_token
            
            logger.debug(f"💳 Charging payment token: {credits_to_charge} credits, token: {'found' if payment_token else 'not found'}")
            
            if not payment_token:
                logger.debug("💳 No payment token to charge")
                return
            
            # Import here to avoid circular dependencies
            import httpx
            from robutler.settings import settings
            from robutler.server.base import get_context
            
            portal_url = settings.robutler_portal_url
            
            # Determine which API key to use based on use_robutler_key flag
            if use_robutler_key:
                # Use ROBUTLER_API_KEY from environment for LLM token charges
                import os
                api_key = os.getenv('ROBUTLER_API_KEY', settings.api_key)
                key_source = "ROBUTLER_API_KEY"
            else:
                # Use agent's API key for tool/other charges
                if agent_api_key:
                    api_key = agent_api_key
                    key_source = "provided agent_api_key"
                else:
                    # Get agent's API key from request state
                    agent_api_key_from_state = None
                    if hasattr(request, 'state') and hasattr(request.state, 'agent_state'):
                        agent_state = request.state.agent_state
                        agent_api_key_from_state = agent_state.get('api_key')
                    
                    api_key = agent_api_key_from_state or settings.api_key
                    key_source = "agent state" if agent_api_key_from_state else "settings fallback"
            
            logger.debug(f"💳 Using API key from: {key_source}")
            
            # Get callbacks from context
            context = get_context()
            callbacks = context.get('pricing_callbacks', {}) if context else {}
            on_success = callbacks.get('on_success')
            on_fail = callbacks.get('on_fail')
            
            # Get user info for callbacks
            peer_user_id = context.get_peer_user_id() if context else "anonymous"
            
            # The portal supports API keys as Bearer tokens, so we can use the API key directly
            
            logger.debug(f"💳 Charging token via portal: {portal_url}/api/token/redeem")
            logger.debug(f"💳 Request payload: amount={credits_to_charge}, token=***")
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{portal_url}/api/token/redeem",
                        json={
                            "token": payment_token,
                            "amount": str(credits_to_charge),  # Convert to string for decimal precision
                            "receipt": f"{'LLM token' if use_robutler_key else 'Tool/other'} usage: {credits_to_charge} credits"
                        },
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        redeem_data = response.json()
                        logger.debug(f"💳 Portal redeem response: {redeem_data}")
                        
                        # Extract remaining balance from token response
                        token_data = redeem_data.get('token', {})
                        remaining_balance = token_data.get('availableAmount', 'unknown')
                        
                        logger.info(f"💳 Payment token charged: {credits_to_charge} credits")
                        logger.info(f"   Remaining balance: {remaining_balance} credits")
                        
                        # Call success callback if provided
                        if on_success:
                            try:
                                callback_metadata = {
                                    'remaining_balance': remaining_balance,
                                    'redeem_data': redeem_data,
                                    'use_robutler_key': use_robutler_key,
                                    'key_source': key_source
                                }
                                
                                if asyncio.iscoroutinefunction(on_success):
                                    await on_success(credits_to_charge, peer_user_id, callback_metadata)
                                else:
                                    on_success(credits_to_charge, peer_user_id, callback_metadata)
                                    
                                logger.debug(f"💳 Success callback executed for {credits_to_charge} credits")
                            except Exception as e:
                                logger.error(f"💳 Error in success callback: {e}")
                        
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        logger.error(f"⚠️ Failed to charge payment token: {error_msg}")
                        
                        # Call fail callback if provided
                        if on_fail:
                            try:
                                callback_metadata = {
                                    'status_code': response.status_code,
                                    'response_text': response.text,
                                    'use_robutler_key': use_robutler_key,
                                    'key_source': key_source
                                }
                                
                                if asyncio.iscoroutinefunction(on_fail):
                                    await on_fail(credits_to_charge, error_msg, callback_metadata)
                                else:
                                    on_fail(credits_to_charge, error_msg, callback_metadata)
                                    
                                logger.debug(f"💳 Fail callback executed for {credits_to_charge} credits")
                            except Exception as e:
                                logger.error(f"💳 Error in fail callback: {e}")
                        
                except httpx.TimeoutException:
                    error_msg = "Request timeout"
                    logger.error("⚠️ Timeout charging payment token")
                    
                    # Call fail callback if provided
                    if on_fail:
                        try:
                            callback_metadata = {
                                'error_type': 'timeout',
                                'use_robutler_key': use_robutler_key,
                                'key_source': key_source
                            }
                            
                            if asyncio.iscoroutinefunction(on_fail):
                                await on_fail(credits_to_charge, error_msg, callback_metadata)
                            else:
                                on_fail(credits_to_charge, error_msg, callback_metadata)
                                
                            logger.debug(f"💳 Fail callback executed for timeout")
                        except Exception as e:
                            logger.error(f"💳 Error in fail callback: {e}")
                            
                except httpx.RequestError as e:
                    error_msg = f"Request error: {str(e)}"
                    logger.error(f"⚠️ Request error charging payment token: {e}")
                    
                    # Call fail callback if provided
                    if on_fail:
                        try:
                            callback_metadata = {
                                'error_type': 'request_error',
                                'original_error': str(e),
                                'use_robutler_key': use_robutler_key,
                                'key_source': key_source
                            }
                            
                            if asyncio.iscoroutinefunction(on_fail):
                                await on_fail(credits_to_charge, error_msg, callback_metadata)
                            else:
                                on_fail(credits_to_charge, error_msg, callback_metadata)
                                
                            logger.debug(f"💳 Fail callback executed for request error")
                        except Exception as e:
                            logger.error(f"💳 Error in fail callback: {e}")
                    
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"⚠️ Error charging payment token: {e}")
    
            # Call fail callback if provided and context is available
            try:
                context = get_context()
                if context:
                    callbacks = context.get('pricing_callbacks', {})
                    on_fail = callbacks.get('on_fail')
                    
                    if on_fail:
                        peer_user_id = context.get_peer_user_id()
                        callback_metadata = {
                            'error_type': 'unexpected_error',
                            'original_error': str(e),
                            'use_robutler_key': use_robutler_key
                        }
                        
                        if asyncio.iscoroutinefunction(on_fail):
                            await on_fail(credits_to_charge, error_msg, callback_metadata)
                        else:
                            on_fail(credits_to_charge, error_msg, callback_metadata)
                            
                        logger.debug(f"💳 Fail callback executed for unexpected error")
            except Exception as callback_error:
                logger.error(f"💳 Error in fail callback during exception handling: {callback_error}")
    
    
    
    def _populate_agent_state(self, request, agent_instance, agent_name, messages, stream):
        """Populate unified agent state for both static and dynamic agents."""
        import time
        from datetime import datetime
        from robutler.settings import settings
        from robutler.server.base import RequestState
        
        # Store timing info
        request.state.start_time = time.time()
        
        # Extract payment token from request headers for charging
        payment_token = request.headers.get('x-payment-token') or request.headers.get('X-Payment-Token')
        if payment_token:
            request.state.payment_token = payment_token
        
        # Extract origin identity from request headers
        origin_identity = request.headers.get('x-origin-identity') or request.headers.get('X-Origin-Identity')
        if origin_identity:
            request.state.origin_identity = origin_identity
        
        # Extract peer identity from request headers
        peer_identity = request.headers.get('x-peer-identity') or request.headers.get('X-Peer-Identity')
        if peer_identity:
            request.state.peer_identity = peer_identity
        
        # Determine agent type and get appropriate API key
        agent_type = getattr(agent_instance, '_agent_type', 'static')
        
        # Get API key - prefer agent's own API key, fallback to settings
        api_key = settings.api_key  # Default fallback
        if hasattr(agent_instance, 'api_key') and agent_instance.api_key:
            api_key = agent_instance.api_key
        elif hasattr(agent_instance, '_portal_data'):
            portal_data = agent_instance._portal_data
            if portal_data and portal_data.get('api_key'):
                api_key = portal_data['api_key']
        
        # Create agent state data
        agent_state = {
            'name': agent_name,
            'instance': agent_instance,
            'messages': messages,
            'is_streaming': stream,
            'type': agent_type,
            'method': request.method,
            'path': request.url.path,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'api_key': api_key  # Use agent-specific API key for charging
        }
        
        # Add portal data for dynamic agents
        if agent_type == 'dynamic' and hasattr(agent_instance, '_portal_data'):
            agent_state['portal_data'] = agent_instance._portal_data
            # Extract agent owner info for easier access
            portal_data = agent_instance._portal_data
            if portal_data:
                agent_state['agent_owner_user_id'] = portal_data.get('userId', portal_data.get('ownerId', 'unknown'))
        else:
            # For static agents, owner is typically the system/service
            agent_state['agent_owner_user_id'] = 'system'
        
        # Agent pricing info (all agents are RobutlerAgents)
        if hasattr(agent_instance, 'get_pricing_info'):
            agent_state['pricing_info'] = agent_instance.get_pricing_info()
        
        # Store agent state using BOTH methods for backward compatibility and consistency
        request.state.agent_state = agent_state  # Direct assignment (existing code compatibility)
        
        # Also store through RequestState for consistent context.get() access
        context = RequestState(request)
        context.set('agent_state', agent_state)
        context.set('agent_name', agent_name)
        context.set('agent_instance', agent_instance)
        context.set('agent_api_key', api_key)
        context.set('agent_type', agent_type)
    
    def _create_agent_endpoints(self, agents: List):
        """Create endpoints for registered agents."""
        for agent in agents:
            agent_name = getattr(agent, 'name', str(agent))
            
            # Create agent-specific endpoints using base class functionality
            @self.agent(agent_name)
            async def agent_handler(messages, stream=False, current_agent=agent, current_agent_name=agent_name):
                # Store agent state for usage tracking
                request = _current_request.get()
                if request:
                    self._populate_agent_state(request, current_agent, current_agent_name, messages, stream)
                
                # Check if this is an OpenAI Agent
                try:
                    from agents import Agent
                    if isinstance(current_agent, Agent):
                        # This is an OpenAI Agent - use Runner to execute it
                        from agents import Runner, RunConfig, ModelSettings
                        
                        # Configure model settings to include usage information
                        model_settings = ModelSettings(include_usage=True)
                        run_config = RunConfig(model_settings=model_settings)
                        
                        if stream:
                            # For streaming, use run_streamed (returns RunResultStreaming)
                            result = Runner.run_streamed(current_agent, messages, run_config=run_config)
                            # Store the result for finalize callback access
                            if request:
                                request.state.streaming_result = result
                            return result
                        else:
                            # For non-streaming, use run
                            result = await Runner.run(current_agent, messages, run_config=run_config)
                            # Store the result for finalize callback access
                            if request:
                                request.state.agent_result = result
                            return result.final_output
                except ImportError:
                    # OpenAI agents library not available, fall through to other checks
                    pass
                
                # Check for RobutlerAgent or similar with run method
                if hasattr(current_agent, 'run'):
                    if stream:
                        return await current_agent.run_streamed(messages)
                    else:
                        result = await current_agent.run(messages)
                        return getattr(result, 'final_output', str(result))
                
                # Fallback for other agent types
                else:
                    # Return OpenAI-compatible response for agents without run methods
                    from datetime import datetime
                    import uuid
                    
                    response_content = f"Agent {current_agent_name} processed: {messages[-1]['content'] if messages else 'no messages'}"
                    
                    return {
                        "id": f"chatcmpl-{str(uuid.uuid4())[:8]}",
                        "object": "chat.completion", 
                        "created": int(datetime.utcnow().timestamp()),
                        "model": getattr(current_agent, 'model', 'gpt-4'),
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_content
                            },
                            "finish_reason": "stop"
                        }]
                    } 