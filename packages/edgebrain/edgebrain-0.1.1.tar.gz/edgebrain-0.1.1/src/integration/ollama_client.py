"""
Ollama Integration Layer

This module provides the interface for interacting with Ollama-based LLMs.
It abstracts away the complexities of communicating with Ollama, allowing agents
to seamlessly leverage local LLMs for their reasoning and generation capabilities.
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class OllamaMessage(BaseModel):
    """Represents a message in the conversation with Ollama."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")


class OllamaToolCall(BaseModel):
    """Represents a tool call from Ollama."""
    name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool")


class OllamaResponse(BaseModel):
    """Represents a response from Ollama."""
    content: str = Field(default="", description="Generated text content")
    tool_calls: List[OllamaToolCall] = Field(default_factory=list, description="Tool calls made by the model")
    done: bool = Field(default=True, description="Whether the response is complete")
    model: str = Field(default="", description="Model used for generation")


class OllamaClient:
    """
    Client for interacting with Ollama API.
    
    This class provides methods to communicate with a local Ollama server,
    handle model loading, prompt formatting, and response parsing.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 300):
        """
        Initialize the Ollama client.
        
        Args:
            base_url: Base URL of the Ollama server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _ensure_session(self):
        """Ensure that the session is initialized."""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
    
    async def list_models(self) -> List[str]:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return [model["name"] for model in data.get("models", [])]
                else:
                    logger.error(f"Failed to list models: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful, False otherwise
        """
        await self._ensure_session()
        
        try:
            payload = {"name": model_name}
            async with self.session.post(f"{self.base_url}/api/pull", json=payload) as response:
                if response.status == 200:
                    # Stream the response to handle progress updates
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode())
                                if data.get("status") == "success":
                                    logger.info(f"Successfully pulled model: {model_name}")
                                    return True
                            except json.JSONDecodeError:
                                continue
                    return True
                else:
                    logger.error(f"Failed to pull model {model_name}: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    async def generate(
        self,
        model: str,
        messages: List[OllamaMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> OllamaResponse:
        """
        Generate a response using Ollama.
        
        Args:
            model: Name of the model to use
            messages: List of messages in the conversation
            tools: Optional list of tools available to the model
            stream: Whether to stream the response
            **kwargs: Additional parameters for generation
            
        Returns:
            OllamaResponse object containing the generated content
        """
        await self._ensure_session()
        
        # Convert messages to the format expected by Ollama
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": stream,
            **kwargs
        }
        
        # Add tools if provided
        if tools:
            payload["tools"] = tools
        
        try:
            async with self.session.post(f"{self.base_url}/api/chat", json=payload) as response:
                if response.status == 200:
                    if stream:
                        return await self._handle_streaming_response(response, model)
                    else:
                        data = await response.json()
                        return self._parse_response(data, model)
                else:
                    error_text = await response.text()
                    logger.error(f"Ollama API error {response.status}: {error_text}")
                    return OllamaResponse(content=f"Error: {response.status}", model=model)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return OllamaResponse(content=f"Error: {str(e)}", model=model)
    
    async def _handle_streaming_response(self, response: aiohttp.ClientResponse, model: str) -> OllamaResponse:
        """Handle streaming response from Ollama."""
        content = ""
        tool_calls = []
        
        async for line in response.content:
            if line:
                try:
                    data = json.loads(line.decode())
                    if "message" in data:
                        message = data["message"]
                        if "content" in message:
                            content += message["content"]
                        if "tool_calls" in message:
                            tool_calls.extend(self._parse_tool_calls(message["tool_calls"]))
                    
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        
        return OllamaResponse(content=content, tool_calls=tool_calls, model=model)
    
    def _parse_response(self, data: Dict[str, Any], model: str) -> OllamaResponse:
        """Parse a non-streaming response from Ollama."""
        message = data.get("message", {})
        content = message.get("content", "")
        tool_calls = self._parse_tool_calls(message.get("tool_calls", []))
        
        return OllamaResponse(
            content=content,
            tool_calls=tool_calls,
            done=data.get("done", True),
            model=model
        )
    
    def _parse_tool_calls(self, tool_calls_data: List[Dict[str, Any]]) -> List[OllamaToolCall]:
        """Parse tool calls from Ollama response."""
        tool_calls = []
        for tool_call in tool_calls_data:
            if "function" in tool_call:
                func = tool_call["function"]
                name = func.get("name", "")
                arguments = func.get("arguments", {})
                
                # Parse arguments if they're a string
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                
                tool_calls.append(OllamaToolCall(name=name, arguments=arguments))
        
        return tool_calls
    
    async def check_health(self) -> bool:
        """
        Check if Ollama server is healthy and responsive.
        
        Returns:
            True if server is healthy, False otherwise
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


class OllamaIntegrationLayer:
    """
    High-level integration layer for Ollama.
    
    This class provides a simplified interface for agents to interact with Ollama,
    handling model management, prompt optimization, and response processing.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.1"):
        """
        Initialize the integration layer.
        
        Args:
            base_url: Base URL of the Ollama server
            default_model: Default model to use for generation
        """
        self.client = OllamaClient(base_url)
        self.default_model = default_model
        self._available_models: List[str] = []
        
    async def initialize(self) -> bool:
        """
        Initialize the integration layer.
        
        Returns:
            True if initialization successful, False otherwise
        """
        async with self.client:
            # Check if Ollama is running
            if not await self.client.check_health():
                logger.error("Ollama server is not running or not accessible")
                return False
            
            # Get available models
            self._available_models = await self.client.list_models()
            
            # Ensure default model is available
            if self.default_model not in self._available_models:
                logger.warning(f"Default model {self.default_model} not found. Attempting to pull...")
                if await self.client.pull_model(self.default_model):
                    self._available_models.append(self.default_model)
                else:
                    logger.error(f"Failed to pull default model {self.default_model}")
                    return False
            
            logger.info(f"Ollama integration initialized with {len(self._available_models)} models")
            return True
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> OllamaResponse:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: The main prompt for generation
            context: Optional context from previous interactions
            tools: Optional tools available to the model
            model: Model to use (defaults to default_model)
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            OllamaResponse object
        """
        model = model or self.default_model
        
        # Build messages
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(OllamaMessage(role="system", content=system_prompt))
        
        # Add context if provided
        if context:
            for ctx in context:
                messages.append(OllamaMessage(role="user", content=ctx))
        
        # Add main prompt
        messages.append(OllamaMessage(role="user", content=prompt))
        
        async with self.client:
            return await self.client.generate(
                model=model,
                messages=messages,
                tools=tools,
                **kwargs
            )
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self._available_models.copy()
    
    async def ensure_model_available(self, model_name: str) -> bool:
        """
        Ensure a model is available, pulling it if necessary.
        
        Args:
            model_name: Name of the model to ensure
            
        Returns:
            True if model is available, False otherwise
        """
        if model_name in self._available_models:
            return True
        
        async with self.client:
            if await self.client.pull_model(model_name):
                self._available_models.append(model_name)
                return True
        
        return False

