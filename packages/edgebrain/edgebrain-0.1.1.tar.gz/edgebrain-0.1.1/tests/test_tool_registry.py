"""
Unit tests for Tool Registry
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.tool_registry import (
    ToolRegistry,
    BaseTool,
    Tool,
    WebSearchTool,
    CalculatorTool,
    FileWriteTool,
    FileReadTool
)


class MockTool(BaseTool):
    """Mock tool for testing."""
    
    def __init__(self):
        super().__init__(
            name="mock_tool",
            description="A mock tool for testing",
            category="test"
        )
    
    async def execute(self, param1: str, param2: int = 10) -> dict:
        """Mock execute method."""
        return {
            "param1": param1,
            "param2": param2,
            "success": True
        }


class TestBaseTool:
    """Test BaseTool abstract class."""
    
    def test_tool_creation(self):
        """Test creating a tool."""
        tool = MockTool()
        assert tool.name == "mock_tool"
        assert tool.description == "A mock tool for testing"
        assert tool.category == "test"
    
    def test_get_parameters_schema(self):
        """Test getting parameters schema."""
        tool = MockTool()
        schema = tool.get_parameters_schema()
        
        assert schema["type"] == "object"
        assert "param1" in schema["properties"]
        assert "param2" in schema["properties"]
        assert "param1" in schema["required"]
        assert "param2" not in schema["required"]  # Has default value


@pytest.mark.asyncio
class TestWebSearchTool:
    """Test WebSearchTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = WebSearchTool()
    
    def test_tool_properties(self):
        """Test tool properties."""
        assert self.tool.name == "web_search"
        assert "search" in self.tool.description.lower()
        assert self.tool.category == "information"
    
    async def test_execute(self):
        """Test tool execution."""
        result = await self.tool.execute("test query", max_results=2)
        
        assert result["query"] == "test query"
        assert "results" in result
        assert len(result["results"]) <= 2
        
        # Check result structure
        for res in result["results"]:
            assert "title" in res
            assert "url" in res
            assert "snippet" in res


@pytest.mark.asyncio
class TestCalculatorTool:
    """Test CalculatorTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = CalculatorTool()
    
    def test_tool_properties(self):
        """Test tool properties."""
        assert self.tool.name == "calculator"
        assert "mathematical" in self.tool.description.lower()
        assert self.tool.category == "utility"
    
    async def test_execute_success(self):
        """Test successful calculation."""
        result = await self.tool.execute("2 + 2")
        
        assert result["expression"] == "2 + 2"
        assert result["result"] == 4
        assert result["success"] is True
    
    async def test_execute_failure(self):
        """Test failed calculation."""
        result = await self.tool.execute("invalid expression")
        
        assert result["expression"] == "invalid expression"
        assert "error" in result
        assert result["success"] is False


@pytest.mark.asyncio
class TestFileWriteTool:
    """Test FileWriteTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = FileWriteTool()
    
    def test_tool_properties(self):
        """Test tool properties."""
        assert self.tool.name == "file_write"
        assert "write" in self.tool.description.lower()
        assert self.tool.category == "file_system"
    
    @patch('builtins.open', create=True)
    async def test_execute_success(self, mock_open):
        """Test successful file writing."""
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = await self.tool.execute("test.txt", "Hello, world!")
        
        assert result["filename"] == "test.txt"
        assert result["bytes_written"] > 0
        assert result["success"] is True
        
        mock_open.assert_called_once_with("test.txt", "w")
        mock_file.write.assert_called_once_with("Hello, world!")
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    async def test_execute_failure(self, mock_open):
        """Test failed file writing."""
        result = await self.tool.execute("test.txt", "Hello, world!")
        
        assert result["filename"] == "test.txt"
        assert "error" in result
        assert result["success"] is False


@pytest.mark.asyncio
class TestFileReadTool:
    """Test FileReadTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = FileReadTool()
    
    def test_tool_properties(self):
        """Test tool properties."""
        assert self.tool.name == "file_read"
        assert "read" in self.tool.description.lower()
        assert self.tool.category == "file_system"
    
    @patch('builtins.open', create=True)
    async def test_execute_success(self, mock_open):
        """Test successful file reading."""
        mock_file = Mock()
        mock_file.read.return_value = "Hello, world!"
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = await self.tool.execute("test.txt")
        
        assert result["filename"] == "test.txt"
        assert result["content"] == "Hello, world!"
        assert result["size"] == len("Hello, world!")
        assert result["success"] is True
        
        mock_open.assert_called_once_with("test.txt", "r")
    
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    async def test_execute_failure(self, mock_open):
        """Test failed file reading."""
        result = await self.tool.execute("nonexistent.txt")
        
        assert result["filename"] == "nonexistent.txt"
        assert "error" in result
        assert result["success"] is False


class TestToolRegistry:
    """Test ToolRegistry class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()
    
    def test_initialization(self):
        """Test registry initialization."""
        # Should have default tools registered
        tools = self.registry.get_all_tools()
        assert len(tools) > 0
        
        # Check for default tools
        tool_names = [tool.name for tool in tools]
        assert "web_search" in tool_names
        assert "calculator" in tool_names
        assert "file_write" in tool_names
        assert "file_read" in tool_names
    
    def test_register_tool(self):
        """Test registering a new tool."""
        mock_tool = MockTool()
        initial_count = self.registry.get_tool_count()
        
        self.registry.register_tool(mock_tool)
        
        assert self.registry.get_tool_count() == initial_count + 1
        assert self.registry.get_tool("mock_tool") is not None
        assert "test" in self.registry.get_categories()
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        mock_tool = MockTool()
        self.registry.register_tool(mock_tool)
        initial_count = self.registry.get_tool_count()
        
        success = self.registry.unregister_tool("mock_tool")
        
        assert success is True
        assert self.registry.get_tool_count() == initial_count - 1
        assert self.registry.get_tool("mock_tool") is None
    
    def test_unregister_nonexistent_tool(self):
        """Test unregistering a non-existent tool."""
        success = self.registry.unregister_tool("nonexistent_tool")
        assert success is False
    
    def test_get_tool(self):
        """Test getting a tool by name."""
        tool = self.registry.get_tool("calculator")
        assert tool is not None
        assert tool.name == "calculator"
        
        nonexistent = self.registry.get_tool("nonexistent")
        assert nonexistent is None
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        utility_tools = self.registry.get_tools_by_category("utility")
        assert len(utility_tools) > 0
        
        for tool in utility_tools:
            assert tool.category == "utility"
        
        nonexistent_category = self.registry.get_tools_by_category("nonexistent")
        assert len(nonexistent_category) == 0
    
    def test_get_categories(self):
        """Test getting all categories."""
        categories = self.registry.get_categories()
        assert len(categories) > 0
        assert "utility" in categories
        assert "information" in categories
        assert "file_system" in categories
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self):
        """Test successful tool execution."""
        result = await self.registry.execute_tool(
            "calculator",
            {"expression": "2 + 2"}
        )
        
        assert result["result"] == 4
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            await self.registry.execute_tool("nonexistent", {})
    
    def test_search_tools(self):
        """Test searching for tools."""
        # Search by name
        calc_tools = self.registry.search_tools("calculator")
        assert len(calc_tools) > 0
        assert any(tool.name == "calculator" for tool in calc_tools)
        
        # Search by description
        math_tools = self.registry.search_tools("mathematical")
        assert len(math_tools) > 0
        
        # Search for non-existent
        nonexistent = self.registry.search_tools("nonexistent_term")
        assert len(nonexistent) == 0
    
    def test_validate_tool_parameters_success(self):
        """Test successful parameter validation."""
        # Calculator tool requires 'expression' parameter
        valid = self.registry.validate_tool_parameters(
            "calculator",
            {"expression": "2 + 2"}
        )
        assert valid is True
    
    def test_validate_tool_parameters_missing_required(self):
        """Test parameter validation with missing required parameter."""
        # Calculator tool requires 'expression' parameter
        valid = self.registry.validate_tool_parameters(
            "calculator",
            {}  # Missing required parameter
        )
        assert valid is False
    
    def test_validate_tool_parameters_nonexistent_tool(self):
        """Test parameter validation for non-existent tool."""
        valid = self.registry.validate_tool_parameters(
            "nonexistent",
            {"param": "value"}
        )
        assert valid is False
    
    def test_get_tool_count(self):
        """Test getting tool count."""
        initial_count = self.registry.get_tool_count()
        assert initial_count > 0
        
        # Add a tool
        mock_tool = MockTool()
        self.registry.register_tool(mock_tool)
        
        assert self.registry.get_tool_count() == initial_count + 1
        
        # Remove a tool
        self.registry.unregister_tool("mock_tool")
        
        assert self.registry.get_tool_count() == initial_count


if __name__ == "__main__":
    pytest.main([__file__])

