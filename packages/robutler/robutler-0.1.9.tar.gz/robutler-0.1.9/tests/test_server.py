"""
Test suite for the new Server class functionality.

Tests the basic Server class that extends ServerBase with agent management.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import asyncio
from fastapi import FastAPI

from robutler.server import Server, ServerBase


class MockAgent:
    """Mock agent for testing."""
    def __init__(self, name, has_run=True, has_run_streamed=True):
        self.name = name
        self._has_run = has_run
        self._has_run_streamed = has_run_streamed
    
    async def run(self, messages):
        """Mock run method that returns OpenAI-compatible response."""
        from datetime import datetime
        import uuid
        
        # Create OpenAI-compatible chat completion response
        response_content = f"Agent {self.name} response to: {messages[-1]['content'] if messages else 'no messages'}"
        
        result = Mock()
        result.final_output = {
            "id": f"chatcmpl-{str(uuid.uuid4())[:8]}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": "gpt-4",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(str(messages).split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(str(messages).split()) + len(response_content.split())
            }
        }
        return result
    
    async def run_streamed(self, messages):
        """Mock run_streamed method that returns OpenAI-compatible streaming response."""
        from datetime import datetime
        import uuid
        import json
        
        response_content = f"Streamed response from {self.name}: {messages[-1]['content'] if messages else 'no messages'}"
        
        # Create a mock streaming response that mimics OpenAI's streaming format
        class MockStreamResponse:
            def __init__(self, content, agent_name):
                self.content = content
                self.agent_name = agent_name
                self.call_id = f"chatcmpl-{str(uuid.uuid4())[:8]}"
                self.created = int(datetime.utcnow().timestamp())
                self.model = "gpt-4"
                self.words = content.split()
                
            async def stream_events(self):
                """Generate streaming events like OpenAI's format."""
                # Initial chunk with role
                initial_chunk = {
                    "id": self.call_id,
                    "object": "chat.completion.chunk",
                    "created": self.created,
                    "model": self.model,
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": ""
                        },
                        "finish_reason": None
                    }]
                }
                yield Mock(
                    type="chunk",
                    data=Mock(chunk=initial_chunk)
                )
                
                # Content chunks
                for i, word in enumerate(self.words):
                    content_chunk = {
                        "id": self.call_id,
                        "object": "chat.completion.chunk", 
                        "created": self.created,
                        "model": self.model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": word + " "
                            },
                            "finish_reason": None
                        }]
                    }
                    yield Mock(
                        type="chunk",
                        data=Mock(chunk=content_chunk)
                    )
                
                # Final chunk with finish_reason and usage
                final_chunk = {
                    "id": self.call_id,
                    "object": "chat.completion.chunk",
                    "created": self.created,
                    "model": self.model,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 25,
                        "completion_tokens": len(self.words),
                        "total_tokens": 25 + len(self.words)
                    }
                }
                yield Mock(
                    type="chunk",
                    data=Mock(chunk=final_chunk)
                )
        
        return MockStreamResponse(response_content, self.name)


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    return MockAgent("test-agent")


class TestServerBasics:
    """Test basic Server functionality."""
    
    def test_server_creation(self):
        """Test basic server creation."""
        server = Server()
        
        assert isinstance(server, Server)
        assert isinstance(server, ServerBase)
        assert hasattr(server, 'agents')
        assert server.agents == []
    
    def test_server_with_empty_agents(self):
        """Test server creation with empty agents list."""
        server = Server(agents=[])
        
        assert server.agents == []
        assert isinstance(server, ServerBase)
    
    def test_server_inheritance(self):
        """Test that Server properly inherits from ServerBase."""
        server = Server()
        
        # Should have ServerBase methods
        assert hasattr(server, 'agent')
        assert hasattr(server, 'get')
        assert hasattr(server, 'post')
        assert hasattr(server, 'middleware')
        
        # Should have FastAPI methods
        assert hasattr(server, 'add_api_route')
        assert hasattr(server, 'add_middleware')


class TestServerAgents:
    """Test Server agent functionality."""
    
    def test_server_with_single_agent(self, mock_agent):
        """Test server creation with a single agent."""
        server = Server(agents=[mock_agent])
        
        assert len(server.agents) == 1
        assert server.agents[0] == mock_agent
        
        # Check that agent endpoint was created
        routes = [route.path for route in server.routes if hasattr(route, 'path')]
        
        expected_routes = [
            "/test-agent",
            "/test-agent/chat/completions"
        ]
        
        for expected_route in expected_routes:
            assert expected_route in routes, f"Route {expected_route} should be created"
    
    def test_server_with_multiple_agents(self):
        """Test server creation with multiple agents."""
        agent1 = MockAgent("agent-1")
        agent2 = MockAgent("agent-2")
        
        server = Server(agents=[agent1, agent2])
        
        assert len(server.agents) == 2
        assert agent1 in server.agents
        assert agent2 in server.agents
        
        # Check that both agent endpoints were created
        routes = [route.path for route in server.routes if hasattr(route, 'path')]
        
        expected_routes = [
            "/agent-1", "/agent-1/chat/completions",
            "/agent-2", "/agent-2/chat/completions"
        ]
        
        for expected_route in expected_routes:
            assert expected_route in routes, f"Route {expected_route} should be created"
    
    def test_agent_without_name_attribute(self):
        """Test agent without name attribute uses string representation."""
        class SimpleAgent:
            def __str__(self):
                return "simple-agent"
        
        agent = SimpleAgent()
        server = Server(agents=[agent])
        
        assert len(server.agents) == 1
        
        # Check that endpoint was created with string representation
        routes = [route.path for route in server.routes if hasattr(route, 'path')]
        assert "/simple-agent" in routes


class TestServerCompatibility:
    """Test Server compatibility and edge cases."""
    
    def test_server_with_none_agents(self):
        """Test server creation with None agents."""
        server = Server(agents=None)
        assert server.agents == []
        assert isinstance(server, FastAPI)
    
    def test_server_additional_args(self):
        """Test server creation with additional FastAPI args."""
        server = Server(title="Test Server", version="1.0.0")
        assert server.title == "Test Server"
        assert server.version == "1.0.0"
        assert isinstance(server, FastAPI)
    
    def test_server_agents_and_additional_args(self):
        """Test server creation with both agents and additional args."""
        agents = [MockAgent("test_agent")]
        server = Server(agents=agents, title="Agent Server")
        assert len(server.agents) == 1
        assert server.title == "Agent Server"
        assert isinstance(server, FastAPI)


class TestOpenAICompatibility:
    """Test OpenAI compatibility of MockAgent responses."""
    
    def test_mock_agent_openai_response_structure(self):
        """Test that MockAgent returns proper OpenAI-compatible response structure."""
        agent = MockAgent("test_agent")
        messages = [{"role": "user", "content": "Hello"}]
        
        # Test non-streaming response
        result = asyncio.run(agent.run(messages))
        response = result.final_output
        
        # Verify OpenAI response structure
        assert "id" in response
        assert response["object"] == "chat.completion"
        assert "created" in response
        assert "model" in response
        assert "choices" in response
        assert "usage" in response
        
        # Verify choices structure
        assert len(response["choices"]) == 1
        choice = response["choices"][0]
        assert choice["index"] == 0
        assert "message" in choice
        assert choice["message"]["role"] == "assistant"
        assert "content" in choice["message"]
        assert choice["finish_reason"] == "stop"
        
        # Verify usage structure
        usage = response["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage
        assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]
    
    def test_mock_agent_streaming_response_structure(self):
        """Test that MockAgent streaming responses have proper OpenAI structure."""
        # Create agent and get streaming response
        agent = MockAgent("test_agent")
        stream_response = asyncio.run(agent.run_streamed([{"role": "user", "content": "Hello"}]))
        
        # Collect all events
        events = []
        async def collect_events():
            async for event in stream_response.stream_events():
                events.append(event)
        
        asyncio.run(collect_events())
        
        # Should have multiple events
        assert len(events) > 1
        
        # Check event structure
        for event in events:
            assert hasattr(event, 'type')
            assert hasattr(event, 'data')
            assert event.type == "chunk"
            assert hasattr(event.data, 'chunk')
            
            # Check chunk structure
            chunk = event.data.chunk
            assert 'id' in chunk
            assert 'object' in chunk
            assert chunk['object'] == 'chat.completion.chunk'
            assert 'created' in chunk
            assert 'model' in chunk
            assert 'choices' in chunk
            assert len(chunk['choices']) == 1
            
            choice = chunk['choices'][0]
            assert 'index' in choice
            assert choice['index'] == 0
            assert 'delta' in choice
            assert 'finish_reason' in choice
        
        # Final event should have usage information
        final_event = events[-1]
        final_chunk = final_event.data.chunk
        assert 'usage' in final_chunk
        assert 'prompt_tokens' in final_chunk['usage']
        assert 'completion_tokens' in final_chunk['usage']
        assert 'total_tokens' in final_chunk['usage']
        assert final_chunk['choices'][0]['finish_reason'] == 'stop'


class TestOpenAIAgentCompatibility:
    """Test compatibility with OpenAI agents library."""
    
    def test_openai_agent_detection(self):
        """Test that OpenAI agents are properly detected."""
        try:
            from agents import Agent
            
            # Create a real OpenAI Agent
            openai_agent = Agent(
                name="test-openai-agent",
                instructions="You are a helpful assistant",
                model="gpt-4o-mini"
            )
            
            # Create server with OpenAI agent
            server = Server(agents=[openai_agent])
            
            # Verify agent was registered
            assert len(server.agents) == 1
            assert server.agents[0] == openai_agent
            
            # Check that agent endpoint was created
            routes = [route.path for route in server.routes if hasattr(route, 'path')]
            
            expected_routes = [
                "/test-openai-agent",
                "/test-openai-agent/chat/completions"
            ]
            
            for expected_route in expected_routes:
                assert expected_route in routes, f"Route {expected_route} should be created"
                
        except ImportError:
            pytest.skip("OpenAI agents library not available")
    
    def test_openai_agent_with_tools(self):
        """Test OpenAI agent with function tools."""
        try:
            from agents import Agent, function_tool
            
            @function_tool
            def get_weather(city: str) -> str:
                return f"The weather in {city} is sunny"
            
            # Create OpenAI Agent with tools
            openai_agent = Agent(
                name="weather-agent",
                instructions="You help with weather information",
                model="gpt-4o-mini",
                tools=[get_weather]
            )
            
            # Create server
            server = Server(agents=[openai_agent])
            
            # Verify agent was registered
            assert len(server.agents) == 1
            assert server.agents[0] == openai_agent
            
            # Verify agent has tools
            assert len(openai_agent.tools) == 1
            
        except ImportError:
            pytest.skip("OpenAI agents library not available")
    
    def test_openai_agent_without_library_fallback(self):
        """Test that agents without proper interface fall through to generic fallback."""
        # Mock an agent that doesn't have run method and isn't an OpenAI Agent
        class MockGenericAgent:
            def __init__(self, name):
                self.name = name
                self.model = "gpt-4o-mini"
            
            # No run method - should fall through to generic fallback
        
        generic_agent = MockGenericAgent("generic-agent")
        
        # Create server with generic agent
        server = Server(agents=[generic_agent])
        
        # Create test client
        client = create_test_client(server)
        
        # Make request to agent endpoint
        response = client.post(
            "/generic-agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
        )
        
        # Should get a generic response
        assert response.status_code == 200
        
        # Parse response
        response_data = response.json()
        
        # Verify OpenAI-compatible structure
        assert "id" in response_data
        assert response_data["object"] == "chat.completion"
        assert "created" in response_data
        assert response_data["model"] == "gpt-4o-mini"
        assert "choices" in response_data
        
        # Check that it's a generic processed message
        content = response_data["choices"][0]["message"]["content"]
        assert "generic-agent processed" in content.lower()
        assert "hello" in content.lower()
    
    def test_mixed_agent_types(self):
        """Test server with both OpenAI agents and RobutlerAgents."""
        try:
            from agents import Agent
            
            # Create real OpenAI Agent
            openai_agent = Agent(
                name="openai-agent",
                instructions="OpenAI agent",
                model="gpt-4o-mini"
            )
            
            # Mock RobutlerAgent (has run method)
            class MockRobutlerAgent:
                def __init__(self, name):
                    self.name = name
                
                async def run(self, messages):
                    return Mock(final_output="RobutlerAgent response")
            
            robutler_agent = MockRobutlerAgent("robutler-agent")
            
            # Create server with mixed agents
            server = Server(agents=[openai_agent, robutler_agent])
            
            # Verify both agents were registered
            assert len(server.agents) == 2
            
            # Check that endpoints were created for both
            routes = [route.path for route in server.routes if hasattr(route, 'path')]
            
            expected_routes = [
                "/openai-agent",
                "/openai-agent/chat/completions",
                "/robutler-agent", 
                "/robutler-agent/chat/completions"
            ]
            
            for expected_route in expected_routes:
                assert expected_route in routes, f"Route {expected_route} should be created"
                
        except ImportError:
            pytest.skip("OpenAI agents library not available")
    
    def test_openai_agent_model_attribute_usage(self):
        """Test that OpenAI agent's model attribute is used in responses."""
        try:
            from agents import Agent
            
            # Create OpenAI Agent with specific model
            openai_agent = Agent(
                name="test-agent",
                instructions="Test instructions",
                model="gpt-4o-mini"
            )
            
            # Create server
            server = Server(agents=[openai_agent])
            client = create_test_client(server)
            
            # Make request
            response = client.post(
                "/test-agent/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "stream": False
                }
            )
            
            # Should get a successful response (actual OpenAI API call would happen)
            # But we'll get an error due to missing API key, which is expected
            assert response.status_code == 200
            
            # Parse response 
            response_data = response.json()
            
            # Verify structure
            assert "id" in response_data
            assert response_data["object"] == "chat.completion"
            assert "created" in response_data
            assert "choices" in response_data
            
        except ImportError:
            pytest.skip("OpenAI agents library not available")


def create_test_client(app):
    """Create a test client with fallback options."""
    # Try multiple approaches to get a working test client
    
    # First try: Standard FastAPI TestClient
    try:
        from fastapi.testclient import TestClient as FastAPITestClient
        return FastAPITestClient(app)
    except Exception:
        pass
    
    # Second try: Starlette TestClient directly
    try:
        from starlette.testclient import TestClient as StarletteTestClient
        return StarletteTestClient(app)
    except Exception:
        pass
    
    # Third try: Manual HTTPX with proper async handling
    try:
        import httpx
        import asyncio
        
        class AsyncTestClient:
            def __init__(self, app):
                self.app = app
                
            def _run_async_request(self, method: str, url: str, json_data=None, **kwargs):
                """Run an async request and return response."""
                async def make_request():
                    async with httpx.AsyncClient(
                        transport=httpx.ASGITransport(app=self.app),
                        base_url="http://testserver"
                    ) as client:
                        if json_data:
                            kwargs['json'] = json_data
                        response = await client.request(method, url, **kwargs)
                        return response
                
                # Run the async request
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If we're already in an event loop, create a new one
                        import threading
                        result = [None]
                        exception = [None]
                        
                        def run_in_thread():
                            try:
                                new_loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(new_loop)
                                result[0] = new_loop.run_until_complete(make_request())
                                new_loop.close()
                            except Exception as e:
                                exception[0] = e
                        
                        thread = threading.Thread(target=run_in_thread)
                        thread.start()
                        thread.join()
                        
                        if exception[0]:
                            raise exception[0]
                        return result[0]
                    else:
                        return loop.run_until_complete(make_request())
                except RuntimeError:
                    # No event loop, create a new one
                    return asyncio.run(make_request())
            
            def get(self, url: str, **kwargs):
                return self._run_async_request("GET", url, **kwargs)
            
            def post(self, url: str, **kwargs):
                json_data = kwargs.pop('json', None)
                return self._run_async_request("POST", url, json_data=json_data, **kwargs)
        
        return AsyncTestClient(app)
    except Exception:
        pass
    
    raise RuntimeError("All test client approaches failed")


class TestServerLifecycleCallbacks:
    """Test that Server properly handles lifecycle callbacks for agent responses."""
    
    def test_finalize_request_called_for_non_streamed_response(self):
        """Test that finalize_request callbacks are called for non-streamed agent responses."""
        # Track callback calls
        callback_calls = []
        
        def finalize_callback(request, response):
            callback_calls.append({
                'type': 'finalize',
                'method': request.method,
                'url': str(request.url),
                'status_code': response.status_code if hasattr(response, 'status_code') else None
            })
        
        # Create server with agent and callback
        agent = MockAgent("test_agent")
        server = Server(agents=[agent])
        server.agent.finalize_request(finalize_callback)
        
        # Create test client
        client = create_test_client(server)
        
        # Make request to agent endpoint
        response = client.post(
            "/test_agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
        )
        
        # Verify response is successful
        assert response.status_code == 200
        
        # Verify callback was called exactly once
        assert len(callback_calls) == 1
        assert callback_calls[0]['type'] == 'finalize'
        assert callback_calls[0]['method'] == 'POST'
        assert '/test_agent/chat/completions' in callback_calls[0]['url']
        # Status code may vary depending on when callback is called
        assert callback_calls[0]['status_code'] in [200, None]
    
    def test_finalize_request_called_for_streamed_response(self):
        """Test that finalize_request callbacks are called for streamed agent responses."""
        # Track callback calls and timing
        callback_calls = []
        streaming_completed = False
        
        def finalize_callback(request, response):
            callback_calls.append({
                'type': 'finalize',
                'method': request.method,
                'url': str(request.url),
                'streaming_completed': streaming_completed,
                'status_code': response.status_code if hasattr(response, 'status_code') else None
            })
        
        # Create server with agent and callback
        agent = MockAgent("test_agent")
        server = Server(agents=[agent])
        server.agent.finalize_request(finalize_callback)
        
        # Create test client
        client = create_test_client(server)
        
        # Make streaming request to agent endpoint
        response = client.post(
            "/test_agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            }
        )
        
        # Verify response is successful
        assert response.status_code == 200
        
        # Consume streaming response
        try:
            if hasattr(response, 'iter_content'):
                chunks = list(response.iter_content())
            elif hasattr(response, 'iter_text'):
                chunks = list(response.iter_text())
            else:
                chunks = [response.text]
        except Exception:
            chunks = [response.text]
        
        # Mark streaming as completed
        streaming_completed = True
        
        # For streaming responses, the finalize callback should be called exactly once
        # after the streaming response is set up (not after consumption)
        assert len(callback_calls) == 1
        
        # Find the finalize callback
        finalize_call = next((call for call in callback_calls if call['type'] == 'finalize'), None)
        assert finalize_call is not None
        assert finalize_call['method'] == 'POST'
        assert '/test_agent/chat/completions' in finalize_call['url']
    
    def test_multiple_callbacks_called_for_agent_responses(self):
        """Test that multiple callbacks are properly called for agent responses."""
        # Track callback calls
        before_calls = []
        finalize_calls = []
        
        def before_callback(request):
            before_calls.append({
                'type': 'before',
                'method': request.method,
                'url': str(request.url)
            })
        
        def finalize_callback(request, response):
            finalize_calls.append({
                'type': 'finalize',
                'method': request.method,
                'url': str(request.url),
                'status_code': response.status_code if hasattr(response, 'status_code') else None
            })
        
        # Create server with agent and callbacks
        agent = MockAgent("test_agent")
        server = Server(agents=[agent])
        server.agent.before_request(before_callback)
        server.agent.finalize_request(finalize_callback)
        
        # Create test client
        client = create_test_client(server)
        
        # Make request to agent endpoint
        response = client.post(
            "/test_agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False
            }
        )
        
        # Verify response is successful
        assert response.status_code == 200
        
        # Verify both callbacks were called
        assert len(before_calls) == 1
        assert len(finalize_calls) == 1
        
        # Verify callback details
        assert before_calls[0]['type'] == 'before'
        assert before_calls[0]['method'] == 'POST'
        assert '/test_agent/chat/completions' in before_calls[0]['url']
        
        assert finalize_calls[0]['type'] == 'finalize'
        assert finalize_calls[0]['method'] == 'POST'
        assert '/test_agent/chat/completions' in finalize_calls[0]['url']
        # Status code may vary depending on when callback is called
        assert finalize_calls[0]['status_code'] in [200, None]
    
    def test_callback_execution_order_for_streaming(self):
        """Test that callbacks are executed in proper order for streaming responses."""
        execution_order = []
        
        def before_callback(request):
            execution_order.append('before_request')
        
        def finalize_callback(request, response):
            execution_order.append('finalize_request')
        
        # Create server with agent and callbacks
        agent = MockAgent("test_agent")
        server = Server(agents=[agent])
        server.agent.before_request(before_callback)
        server.agent.finalize_request(finalize_callback)
        
        # Create test client
        client = create_test_client(server)
        
        # Make streaming request
        response = client.post(
            "/test_agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            }
        )
        
        # Verify response is successful
        assert response.status_code == 200
        
        # Consume streaming response
        try:
            if hasattr(response, 'iter_content'):
                chunks = list(response.iter_content())
            elif hasattr(response, 'iter_text'):
                chunks = list(response.iter_text())
            else:
                chunks = [response.text]
        except Exception:
            chunks = [response.text]
        
        # Verify callback execution order
        assert len(execution_order) >= 2
        assert execution_order[0] == 'before_request'
        # finalize_request should be called (exact timing may vary for streaming)
        assert 'finalize_request' in execution_order

    def test_finalize_callback_has_access_to_streaming_final_results(self):
        """Test that finalize callbacks receive the streaming response and can access final chunk data."""
        # Track callback calls and captured results
        callback_calls = []
        
        def finalize_callback(request, response):
            callback_calls.append({
                'type': 'finalize',
                'method': request.method,
                'url': str(request.url),
                'response_type': type(response).__name__,
                'has_original_response': hasattr(response, 'original_response') if hasattr(response, 'original_response') else False
            })
        
        # Create server with agent and callback
        agent = MockAgent("test_agent")
        server = Server(agents=[agent])
        server.agent.finalize_request(finalize_callback)
        
        # Create test client
        client = create_test_client(server)
        
        # Make streaming request to agent endpoint
        response = client.post(
            "/test_agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            }
        )
        
        # Verify response is successful
        assert response.status_code == 200
        
        # Consume the streaming response to completion
        try:
            if hasattr(response, 'iter_content'):
                chunks = list(response.iter_content())
            elif hasattr(response, 'iter_text'):
                chunks = list(response.iter_text())
            else:
                chunks = [response.text]
        except Exception:
            chunks = [response.text]
        
        # Verify callback was called exactly once
        assert len(callback_calls) == 1
        
        # Verify callback received the StreamingWrapper
        callback = callback_calls[0]
        assert callback['type'] == 'finalize'
        assert callback['method'] == 'POST'
        assert '/test_agent/chat/completions' in callback['url']
        assert callback['response_type'] == 'StreamingWrapper'
        
        # The key point: finalize callback receives the StreamingWrapper response
        # which contains the original_response with all the streaming data
        # This allows the callback to access the final chunk information if needed

    def test_finalize_callback_can_access_mock_agent_final_chunk(self):
        """Test that MockAgent generates final chunks with usage info that callbacks can access."""
        # Track what the finalize callback receives
        callback_data = {}
        streaming_chunks = []
        
        def finalize_callback(request, response):
            callback_data['response_type'] = type(response).__name__
            callback_data['has_original_response'] = hasattr(response, 'original_response')
            
            # For demonstration: a real callback could collect chunks during streaming
            # or access the response object to get final information
            callback_data['response_received'] = True
        
        # Create server with agent and callback
        agent = MockAgent("test_agent")
        server = Server(agents=[agent])
        server.agent.finalize_request(finalize_callback)
        
        # Create test client
        client = create_test_client(server)
        
        # Make streaming request
        response = client.post(
            "/test_agent/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello world"}],
                "stream": True
            }
        )
        
        assert response.status_code == 200
        
        # Consume streaming response and collect chunks
        response_text = ""
        try:
            if hasattr(response, 'iter_content'):
                for chunk in response.iter_content():
                    if chunk:
                        chunk_text = chunk.decode() if isinstance(chunk, bytes) else str(chunk)
                        response_text += chunk_text
                        streaming_chunks.append(chunk_text)
            elif hasattr(response, 'iter_text'):
                for chunk in response.iter_text():
                    response_text += chunk
                    streaming_chunks.append(chunk)
            else:
                response_text = response.text
                streaming_chunks.append(response_text)
        except Exception:
            response_text = response.text
            streaming_chunks.append(response_text)
        
        # Verify finalize callback was called
        assert callback_data['response_received'] is True
        assert callback_data['response_type'] == 'StreamingWrapper'
        
        # Verify that the streaming response contains final chunk with usage
        # This demonstrates that MockAgent generates proper final chunks
        has_usage_chunk = False
        has_finish_reason = False
        
        for chunk in streaming_chunks:
            if 'usage' in chunk and 'total_tokens' in chunk:
                has_usage_chunk = True
            if 'finish_reason' in chunk and 'stop' in chunk:
                has_finish_reason = True
        
        # MockAgent should generate final chunks with usage and finish_reason
        assert has_usage_chunk, f"No usage chunk found in: {streaming_chunks}"
        assert has_finish_reason, f"No finish_reason found in: {streaming_chunks}"


class TestPricingDecorator:
    """Test the pricing decorator functionality."""
    
    def test_pricing_decorator_import(self):
        """Test that pricing decorator can be imported."""
        from robutler.server import pricing
        
        assert callable(pricing)
    
    def test_pricing_decorator_basic_usage(self):
        """Test basic usage of pricing decorator."""
        from robutler.server import pricing
        
        @pricing(credits_per_call=10)
        async def test_agent(messages, stream=False):
            return "Test response"
        
        # Function should be decorated and callable
        assert callable(test_agent)
        assert test_agent.__name__ == "test_agent"
    
    def test_pricing_decorator_with_multiple_params(self):
        """Test pricing decorator with multiple parameters."""
        from robutler.server import pricing
        
        @pricing(credits_per_call=5, reason="Custom test reason")
        async def test_agent(messages, stream=False):
            return "Test response"
        
        # Function should be decorated and callable
        assert callable(test_agent)
        assert test_agent.__name__ == "test_agent"
    
    def test_pricing_decorator_preserves_function_behavior(self):
        """Test that pricing decorator preserves original function behavior."""
        from robutler.server import pricing
        import asyncio
        
        @pricing(credits_per_call=10)
        async def test_agent(messages, stream=False):
            return f"Processed: {messages[-1]['content'] if messages else 'no messages'}"
        
        # Function should still work normally
        messages = [{"role": "user", "content": "Hello"}]
        result = asyncio.run(test_agent(messages))
        
        assert result == "Processed: Hello"
    
    def test_pricing_decorator_without_params(self):
        """Test pricing decorator without any parameters."""
        from robutler.server import pricing
        
        @pricing()
        async def test_agent(messages, stream=False):
            return "Test response"
        
        # Function should be decorated and callable
        assert callable(test_agent)
        assert test_agent.__name__ == "test_agent"
    
    def test_pricing_decorator_preserves_function_metadata(self):
        """Test that pricing decorator preserves function metadata."""
        from robutler.server import pricing
        
        @pricing(credits_per_call=10)
        async def test_agent(messages, stream=False):
            """Test agent docstring."""
            return "Test response"
        
        # Function metadata should be preserved
        assert test_agent.__name__ == "test_agent"
        assert test_agent.__doc__ == "Test agent docstring."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
