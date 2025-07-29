"""
Unit tests for Ollama Integration Layer
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integration.ollama_client import (
    OllamaClient, 
    OllamaIntegrationLayer, 
    OllamaMessage, 
    OllamaResponse,
    OllamaToolCall
)


class TestOllamaMessage:
    """Test OllamaMessage model."""
    
    def test_create_message(self):
        """Test creating a message."""
        message = OllamaMessage(role="user", content="Hello, world!")
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_message_validation(self):
        """Test message validation."""
        with pytest.raises(ValueError):
            OllamaMessage(content="Missing role")


class TestOllamaResponse:
    """Test OllamaResponse model."""
    
    def test_create_response(self):
        """Test creating a response."""
        response = OllamaResponse(
            content="Hello!",
            model="llama3.1",
            done=True
        )
        assert response.content == "Hello!"
        assert response.model == "llama3.1"
        assert response.done is True
        assert response.tool_calls == []
    
    def test_response_with_tool_calls(self):
        """Test response with tool calls."""
        tool_call = OllamaToolCall(name="calculator", arguments={"expression": "2+2"})
        response = OllamaResponse(
            content="I'll calculate that for you.",
            tool_calls=[tool_call],
            model="llama3.1"
        )
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "calculator"


@pytest.mark.asyncio
class TestOllamaClient:
    """Test OllamaClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = OllamaClient(base_url="http://localhost:11434")
    
    @patch('aiohttp.ClientSession.get')
    async def test_list_models_success(self, mock_get):
        """Test successful model listing."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.1"},
                {"name": "mistral"}
            ]
        }
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with self.client:
            models = await self.client.list_models()
        
        assert models == ["llama3.1", "mistral"]
    
    @patch('aiohttp.ClientSession.get')
    async def test_list_models_failure(self, mock_get):
        """Test failed model listing."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with self.client:
            models = await self.client.list_models()
        
        assert models == []
    
    @patch('aiohttp.ClientSession.get')
    async def test_health_check_success(self, mock_get):
        """Test successful health check."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with self.client:
            is_healthy = await self.client.check_health()
        
        assert is_healthy is True
    
    @patch('aiohttp.ClientSession.get')
    async def test_health_check_failure(self, mock_get):
        """Test failed health check."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with self.client:
            is_healthy = await self.client.check_health()
        
        assert is_healthy is False
    
    @patch('aiohttp.ClientSession.post')
    async def test_generate_success(self, mock_post):
        """Test successful generation."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "message": {
                "content": "Hello! How can I help you today?"
            },
            "done": True
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        messages = [OllamaMessage(role="user", content="Hello")]
        
        async with self.client:
            response = await self.client.generate("llama3.1", messages)
        
        assert response.content == "Hello! How can I help you today?"
        assert response.model == "llama3.1"
        assert response.done is True
    
    @patch('aiohttp.ClientSession.post')
    async def test_generate_with_tools(self, mock_post):
        """Test generation with tool calls."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "message": {
                "content": "I'll calculate that for you.",
                "tool_calls": [
                    {
                        "function": {
                            "name": "calculator",
                            "arguments": '{"expression": "2+2"}'
                        }
                    }
                ]
            },
            "done": True
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        messages = [OllamaMessage(role="user", content="What is 2+2?")]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Perform calculations"
                }
            }
        ]
        
        async with self.client:
            response = await self.client.generate("llama3.1", messages, tools=tools)
        
        assert response.content == "I'll calculate that for you."
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "calculator"
        assert response.tool_calls[0].arguments == {"expression": "2+2"}


@pytest.mark.asyncio
class TestOllamaIntegrationLayer:
    """Test OllamaIntegrationLayer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.integration = OllamaIntegrationLayer(
            base_url="http://localhost:11434",
            default_model="llama3.1"
        )
    
    @patch.object(OllamaClient, 'check_health')
    @patch.object(OllamaClient, 'list_models')
    @patch.object(OllamaClient, 'pull_model')
    async def test_initialize_success(self, mock_pull, mock_list, mock_health):
        """Test successful initialization."""
        mock_health.return_value = True
        mock_list.return_value = ["llama3.1", "mistral"]
        
        success = await self.integration.initialize()
        
        assert success is True
        assert "llama3.1" in self.integration.get_available_models()
        mock_pull.assert_not_called()  # Model already available
    
    @patch.object(OllamaClient, 'check_health')
    @patch.object(OllamaClient, 'list_models')
    @patch.object(OllamaClient, 'pull_model')
    async def test_initialize_pull_default_model(self, mock_pull, mock_list, mock_health):
        """Test initialization with pulling default model."""
        mock_health.return_value = True
        mock_list.return_value = ["mistral"]  # Default model not available
        mock_pull.return_value = True
        
        success = await self.integration.initialize()
        
        assert success is True
        mock_pull.assert_called_once_with("llama3.1")
    
    @patch.object(OllamaClient, 'check_health')
    async def test_initialize_health_check_failure(self, mock_health):
        """Test initialization failure due to health check."""
        mock_health.return_value = False
        
        success = await self.integration.initialize()
        
        assert success is False
    
    @patch.object(OllamaClient, 'generate')
    async def test_generate_response_simple(self, mock_generate):
        """Test simple response generation."""
        mock_generate.return_value = OllamaResponse(
            content="Hello! How can I help you?",
            model="llama3.1"
        )
        
        response = await self.integration.generate_response("Hello")
        
        assert response.content == "Hello! How can I help you?"
        assert response.model == "llama3.1"
    
    @patch.object(OllamaClient, 'generate')
    async def test_generate_response_with_context(self, mock_generate):
        """Test response generation with context."""
        mock_generate.return_value = OllamaResponse(
            content="Based on our previous conversation...",
            model="llama3.1"
        )
        
        context = ["Previous message 1", "Previous message 2"]
        response = await self.integration.generate_response(
            "Continue our conversation",
            context=context
        )
        
        # Verify that generate was called with the right number of messages
        call_args = mock_generate.call_args
        messages = call_args[1]["messages"]
        
        # Should have context messages plus the main prompt
        assert len(messages) >= len(context) + 1
    
    @patch.object(OllamaClient, 'generate')
    async def test_generate_response_with_system_prompt(self, mock_generate):
        """Test response generation with system prompt."""
        mock_generate.return_value = OllamaResponse(
            content="I am a helpful assistant.",
            model="llama3.1"
        )
        
        response = await self.integration.generate_response(
            "Hello",
            system_prompt="You are a helpful assistant."
        )
        
        # Verify that generate was called with system message
        call_args = mock_generate.call_args
        messages = call_args[1]["messages"]
        
        # First message should be system message
        assert messages[0].role == "system"
        assert "helpful assistant" in messages[0].content
    
    @patch.object(OllamaClient, 'pull_model')
    async def test_ensure_model_available_pull_needed(self, mock_pull):
        """Test ensuring model availability when pull is needed."""
        mock_pull.return_value = True
        
        # Model not in available list initially
        self.integration._available_models = ["llama3.1"]
        
        success = await self.integration.ensure_model_available("mistral")
        
        assert success is True
        assert "mistral" in self.integration.get_available_models()
        mock_pull.assert_called_once_with("mistral")
    
    async def test_ensure_model_available_already_available(self):
        """Test ensuring model availability when already available."""
        # Model already in available list
        self.integration._available_models = ["llama3.1", "mistral"]
        
        success = await self.integration.ensure_model_available("mistral")
        
        assert success is True
    
    def test_get_available_models(self):
        """Test getting available models."""
        self.integration._available_models = ["llama3.1", "mistral"]
        
        models = self.integration.get_available_models()
        
        assert models == ["llama3.1", "mistral"]
        # Ensure it returns a copy, not the original list
        models.append("new_model")
        assert "new_model" not in self.integration.get_available_models()


if __name__ == "__main__":
    pytest.main([__file__])

