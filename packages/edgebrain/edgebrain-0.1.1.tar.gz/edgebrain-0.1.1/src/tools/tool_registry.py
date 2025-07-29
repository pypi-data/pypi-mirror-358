"""
Tool Registry Implementation

This module provides a centralized repository for all available tools that agents can utilize.
It provides a standardized interface for agents to discover and invoke tools.
"""

import asyncio
import inspect
from typing import Dict, List, Optional, Any, Callable, Union
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Represents a parameter for a tool."""
    name: str = Field(..., description="Name of the parameter")
    type: str = Field(..., description="Type of the parameter")
    description: str = Field(..., description="Description of the parameter")
    required: bool = Field(default=True, description="Whether the parameter is required")
    default: Any = Field(None, description="Default value for the parameter")


class Tool(BaseModel):
    """Represents a tool that can be used by agents."""
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for tool parameters")
    category: str = Field(default="general", description="Category of the tool")
    version: str = Field(default="1.0.0", description="Version of the tool")
    
    class Config:
        arbitrary_types_allowed = True


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    All tools must inherit from this class and implement the execute method.
    """
    
    def __init__(self, name: str, description: str, category: str = "general"):
        """
        Initialize the tool.
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
            category: Category of the tool
        """
        self.name = name
        self.description = description
        self.category = category
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Parameters for tool execution
            
        Returns:
            Result of tool execution
        """
        pass
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for the tool's parameters.
        
        Returns:
            JSON schema describing the tool's parameters
        """
        # Get the execute method signature
        sig = inspect.signature(self.execute)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
                
            param_type = "string"  # Default type
            param_desc = f"Parameter {param_name}"
            
            # Try to extract type information
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"
            
            properties[param_name] = {
                "type": param_type,
                "description": param_desc
            }
            
            # Check if parameter is required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }


class WebSearchTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information on a given query",
            category="information"
        )
    
    async def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Perform a web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Search results
        """
        # This is a mock implementation
        # In a real implementation, you would integrate with a search API
        await asyncio.sleep(0.5)  # Simulate API call
        
        return {
            "query": query,
            "results": [
                {
                    "title": f"Result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a mock search result {i+1} for the query '{query}'"
                }
                for i in range(min(max_results, 3))
            ]
        }


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations",
            category="utility"
        )
    
    async def execute(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Result of the calculation
        """
        try:
            # Simple evaluation (in production, use a safer math parser)
            result = eval(expression)
            return {
                "expression": expression,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False
            }


class FileWriteTool(BaseTool):
    """Tool for writing content to files."""
    
    def __init__(self):
        super().__init__(
            name="file_write",
            description="Write content to a file",
            category="file_system"
        )
    
    async def execute(self, filename: str, content: str, mode: str = "w") -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            filename: Name of the file to write
            content: Content to write to the file
            mode: File mode (w for write, a for append)
            
        Returns:
            Result of the file operation
        """
        try:
            with open(filename, mode) as f:
                f.write(content)
            
            return {
                "filename": filename,
                "bytes_written": len(content.encode()),
                "success": True
            }
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "success": False
            }


class FileReadTool(BaseTool):
    """Tool for reading content from files."""
    
    def __init__(self):
        super().__init__(
            name="file_read",
            description="Read content from a file",
            category="file_system"
        )
    
    async def execute(self, filename: str) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            filename: Name of the file to read
            
        Returns:
            Content of the file
        """
        try:
            with open(filename, "r") as f:
                content = f.read()
            
            return {
                "filename": filename,
                "content": content,
                "size": len(content),
                "success": True
            }
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "success": False
            }


class ToolRegistry:
    """
    Centralized registry for all available tools.
    
    Provides a standardized interface for agents to discover and invoke tools.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {}
        
        # Register default tools
        self._register_default_tools()
        
        logger.info("Tool registry initialized")
    
    def _register_default_tools(self):
        """Register default tools."""
        default_tools = [
            WebSearchTool(),
            CalculatorTool(),
            FileWriteTool(),
            FileReadTool()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a new tool.
        
        Args:
            tool: Tool to register
        """
        self._tools[tool.name] = tool
        
        # Add to category
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        
        if tool.name not in self._categories[tool.category]:
            self._categories[tool.category].append(tool.name)
        
        logger.info(f"Registered tool: {tool.name} (category: {tool.category})")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name in self._tools:
            tool = self._tools[tool_name]
            del self._tools[tool_name]
            
            # Remove from category
            if tool.category in self._categories:
                if tool_name in self._categories[tool.category]:
                    self._categories[tool.category].remove(tool_name)
                
                # Remove empty category
                if not self._categories[tool.category]:
                    del self._categories[tool.category]
            
            logger.info(f"Unregistered tool: {tool_name}")
            return True
        
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> List[Tool]:
        """
        Get all registered tools.
        
        Returns:
            List of all tools
        """
        tools = []
        for tool_name, tool_instance in self._tools.items():
            tool_info = Tool(
                name=tool_instance.name,
                description=tool_instance.description,
                parameters=tool_instance.get_parameters_schema(),
                category=tool_instance.category
            )
            tools.append(tool_info)
        
        return tools
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """
        Get tools by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tools in the specified category
        """
        if category not in self._categories:
            return []
        
        tools = []
        for tool_name in self._categories[category]:
            if tool_name in self._tools:
                tool_instance = self._tools[tool_name]
                tool_info = Tool(
                    name=tool_instance.name,
                    description=tool_instance.description,
                    parameters=tool_instance.get_parameters_schema(),
                    category=tool_instance.category
                )
                tools.append(tool_info)
        
        return tools
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories.
        
        Returns:
            List of category names
        """
        return list(self._categories.keys())
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for tool execution
            
        Returns:
            Result of tool execution
            
        Raises:
            ValueError: If tool is not found
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            result = await tool.execute(**parameters)
            logger.info(f"Executed tool {tool_name} successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def search_tools(self, query: str) -> List[Tool]:
        """
        Search for tools by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        matching_tools = []
        
        for tool_instance in self._tools.values():
            if (query_lower in tool_instance.name.lower() or 
                query_lower in tool_instance.description.lower()):
                
                tool_info = Tool(
                    name=tool_instance.name,
                    description=tool_instance.description,
                    parameters=tool_instance.get_parameters_schema(),
                    category=tool_instance.category
                )
                matching_tools.append(tool_info)
        
        return matching_tools
    
    def get_tool_count(self) -> int:
        """Get the total number of registered tools."""
        return len(self._tools)
    
    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for a tool.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        
        schema = tool.get_parameters_schema()
        required_params = schema.get("required", [])
        
        # Check if all required parameters are present
        for param in required_params:
            if param not in parameters:
                logger.warning(f"Missing required parameter '{param}' for tool '{tool_name}'")
                return False
        
        return True

