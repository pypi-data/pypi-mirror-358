# API Reference

This document provides a comprehensive reference for all classes, methods, and functions in the EdgeBrain framework.

## Table of Contents

- [Core Components](#core-components)
  - [AgentOrchestrator](#agentorchestrator)
  - [Agent](#agent)
- [Integration](#integration)
  - [OllamaIntegrationLayer](#ollamaintegrationlayer)
  - [OllamaClient](#ollamaclient)
- [Tools](#tools)
  - [ToolRegistry](#toolregistry)
  - [BaseTool](#basetool)
- [Memory](#memory)
  - [MemoryManager](#memorymanager)
- [Data Models](#data-models)

## Core Components

### AgentOrchestrator

The central control unit for managing agents and coordinating their interactions.

#### Class Definition

```python
class AgentOrchestrator:
    def __init__(
        self,
        ollama_integration: OllamaIntegrationLayer,
        tool_registry: ToolRegistry,
        memory_manager: MemoryManager
    )
```

#### Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ollama_integration` | `OllamaIntegrationLayer` | Ollama integration layer instance |
| `tool_registry` | `ToolRegistry` | Tool registry for agents |
| `memory_manager` | `MemoryManager` | Memory management system |

#### Methods

##### `async start() -> None`

Start the orchestrator and begin processing tasks and messages.

**Example:**
```python
await orchestrator.start()
```

##### `async stop() -> None`

Stop the orchestrator and clean up resources.

**Example:**
```python
await orchestrator.stop()
```

##### `register_agent(...) -> Agent`

Register a new agent with the orchestrator.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `str` | Yes | Unique identifier for the agent |
| `role` | `str` | Yes | Role of the agent |
| `description` | `str` | Yes | Description of the agent's purpose |
| `model` | `str` | No | Specific model to use for the agent |
| `capabilities` | `List[AgentCapability]` | No | List of agent capabilities |
| `system_prompt` | `str` | No | Custom system prompt for the agent |

**Returns:** `Agent` - The created agent instance

**Example:**
```python
agent = orchestrator.register_agent(
    agent_id="researcher_001",
    role="Research Specialist",
    description="Conducts thorough research on technical topics",
    model="llama3.1",
    capabilities=[
        AgentCapability(name="web_search", description="Search for information"),
        AgentCapability(name="data_analysis", description="Analyze research data")
    ]
)
```

##### `unregister_agent(agent_id: str) -> bool`

Unregister an agent from the orchestrator.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | ID of the agent to unregister |

**Returns:** `bool` - True if agent was unregistered, False if not found

##### `async create_task(...) -> str`

Create a new task for execution.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | `str` | Yes | Description of the task |
| `priority` | `int` | No | Priority of the task (1-10, default: 1) |
| `context` | `Dict[str, Any]` | No | Additional context for the task |

**Returns:** `str` - ID of the created task

**Example:**
```python
task_id = await orchestrator.create_task(
    description="Research current trends in artificial intelligence",
    priority=5,
    context={"topic": "AI trends", "depth": "comprehensive"}
)
```

##### `async assign_task_to_agent(task_id: str, agent_id: str) -> bool`

Assign a task to a specific agent.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | `str` | ID of the task |
| `agent_id` | `str` | ID of the agent |

**Returns:** `bool` - True if assignment successful, False otherwise

##### `async assign_task_to_role(task_id: str, role: str) -> bool`

Assign a task to an agent with a specific role.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | `str` | ID of the task |
| `role` | `str` | Role of the agent to assign to |

**Returns:** `bool` - True if assignment successful, False otherwise

##### `async execute_workflow(workflow: Workflow) -> bool`

Execute a workflow with multiple steps.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `workflow` | `Workflow` | Workflow to execute |

**Returns:** `bool` - True if workflow started successfully, False otherwise

##### `async send_message(...) -> None`

Send a message between agents.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `sender_id` | `str` | ID of the sender |
| `recipient_id` | `str` | ID of the recipient |
| `content` | `str` | Content of the message |
| `message_type` | `str` | Type of the message (default: "text") |

##### `get_agent(agent_id: str) -> Optional[Agent]`

Get an agent by ID.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | ID of the agent |

**Returns:** `Optional[Agent]` - Agent instance or None if not found

##### `get_agents_by_role(role: str) -> List[Agent]`

Get all agents with a specific role.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `role` | `str` | Role to search for |

**Returns:** `List[Agent]` - List of agents with the specified role

##### `get_all_agents() -> List[Agent]`

Get all registered agents.

**Returns:** `List[Agent]` - List of all agents

##### `get_task(task_id: str) -> Optional[Task]`

Get a task by ID.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | `str` | ID of the task |

**Returns:** `Optional[Task]` - Task instance or None if not found

##### `get_all_tasks() -> List[Task]`

Get all tasks.

**Returns:** `List[Task]` - List of all tasks

##### `get_agent_status_summary() -> Dict[str, int]`

Get a summary of agent statuses.

**Returns:** `Dict[str, int]` - Dictionary mapping status names to counts

##### `get_task_status_summary() -> Dict[str, int]`

Get a summary of task statuses.

**Returns:** `Dict[str, int]` - Dictionary mapping status names to counts

### Agent

Represents an autonomous AI agent with specific capabilities and behavior.

#### Class Definition

```python
class Agent:
    def __init__(
        self,
        agent_id: str,
        role: str,
        description: str,
        ollama_integration: OllamaIntegrationLayer,
        tool_registry: ToolRegistry,
        memory_manager: MemoryManager,
        model: Optional[str] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        system_prompt: Optional[str] = None
    )
```

#### Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `str` | Yes | Unique identifier for the agent |
| `role` | `str` | Yes | Role of the agent |
| `description` | `str` | Yes | Description of the agent's purpose |
| `ollama_integration` | `OllamaIntegrationLayer` | Yes | Ollama integration layer |
| `tool_registry` | `ToolRegistry` | Yes | Tool registry for the agent |
| `memory_manager` | `MemoryManager` | Yes | Memory management system |
| `model` | `str` | No | Specific model to use |
| `capabilities` | `List[AgentCapability]` | No | List of agent capabilities |
| `system_prompt` | `str` | No | Custom system prompt |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `agent_id` | `str` | Unique identifier of the agent |
| `role` | `str` | Role of the agent |
| `description` | `str` | Description of the agent |
| `capabilities` | `List[AgentCapability]` | List of agent capabilities |
| `model` | `str` | Model used by the agent |

#### Methods

##### `async set_goal(goal: AgentGoal) -> None`

Set a goal for the agent to work towards.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `goal` | `AgentGoal` | Goal to set for the agent |

##### `async execute_goal() -> bool`

Execute the current goal.

**Returns:** `bool` - True if goal completed successfully, False otherwise

##### `get_status() -> AgentStatus`

Get the current status of the agent.

**Returns:** `AgentStatus` - Current agent status

##### `async process_message(message: AgentMessage) -> None`

Process an incoming message.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `AgentMessage` | Message to process |

##### `async think(context: str) -> str`

Generate thoughts based on the given context.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `context` | `str` | Context for thinking |

**Returns:** `str` - Generated thoughts

##### `async act(action_plan: str) -> bool`

Execute an action based on the action plan.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `action_plan` | `str` | Plan for action execution |

**Returns:** `bool` - True if action successful, False otherwise

## Integration

### OllamaIntegrationLayer

High-level interface for interacting with Ollama models.

#### Class Definition

```python
class OllamaIntegrationLayer:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.1",
        timeout: int = 30
    )
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `"http://localhost:11434"` | Ollama server URL |
| `default_model` | `str` | `"llama3.1"` | Default model to use |
| `timeout` | `int` | `30` | Request timeout in seconds |

#### Methods

##### `async initialize() -> bool`

Initialize the integration layer and check connectivity.

**Returns:** `bool` - True if initialization successful, False otherwise

##### `async generate_response(...) -> OllamaResponse`

Generate a response using the specified model.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | `str` | Yes | Input prompt |
| `model` | `str` | No | Model to use (defaults to default_model) |
| `system_prompt` | `str` | No | System prompt for context |
| `context` | `List[str]` | No | Previous conversation context |
| `tools` | `List[dict]` | No | Available tools for the model |
| `temperature` | `float` | No | Sampling temperature |
| `max_tokens` | `int` | No | Maximum tokens to generate |

**Returns:** `OllamaResponse` - Generated response

**Example:**
```python
response = await ollama_integration.generate_response(
    prompt="What are the latest trends in AI?",
    model="llama3.1",
    system_prompt="You are a research assistant.",
    temperature=0.7
)
```

##### `async ensure_model_available(model: str) -> bool`

Ensure a model is available, downloading if necessary.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str` | Model name to ensure availability |

**Returns:** `bool` - True if model is available, False otherwise

##### `get_available_models() -> List[str]`

Get list of available models.

**Returns:** `List[str]` - List of available model names

### OllamaClient

Low-level client for direct Ollama API interaction.

#### Class Definition

```python
class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 30
    )
```

#### Methods

##### `async check_health() -> bool`

Check if Ollama server is healthy.

**Returns:** `bool` - True if server is healthy, False otherwise

##### `async list_models() -> List[str]`

List all available models.

**Returns:** `List[str]` - List of model names

##### `async pull_model(model: str) -> bool`

Pull a model from the Ollama registry.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `str` | Model name to pull |

**Returns:** `bool` - True if pull successful, False otherwise

##### `async generate(...) -> OllamaResponse`

Generate a response using the Ollama API.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | `str` | Yes | Model to use |
| `messages` | `List[OllamaMessage]` | Yes | Conversation messages |
| `tools` | `List[dict]` | No | Available tools |
| `stream` | `bool` | No | Whether to stream the response |

**Returns:** `OllamaResponse` - Generated response

## Tools

### ToolRegistry

Registry for managing and executing tools that agents can use.

#### Class Definition

```python
class ToolRegistry:
    def __init__(self)
```

#### Methods

##### `register_tool(tool: BaseTool) -> None`

Register a new tool.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tool` | `BaseTool` | Tool to register |

##### `unregister_tool(tool_name: str) -> bool`

Unregister a tool.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Name of the tool to unregister |

**Returns:** `bool` - True if tool was unregistered, False if not found

##### `get_tool(tool_name: str) -> Optional[BaseTool]`

Get a tool by name.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Name of the tool |

**Returns:** `Optional[BaseTool]` - Tool instance or None if not found

##### `get_all_tools() -> List[BaseTool]`

Get all registered tools.

**Returns:** `List[BaseTool]` - List of all tools

##### `get_tools_by_category(category: str) -> List[BaseTool]`

Get tools by category.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | `str` | Category to filter by |

**Returns:** `List[BaseTool]` - List of tools in the category

##### `get_categories() -> List[str]`

Get all tool categories.

**Returns:** `List[str]` - List of category names

##### `async execute_tool(tool_name: str, parameters: dict) -> dict`

Execute a tool with given parameters.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Name of the tool to execute |
| `parameters` | `dict` | Parameters for tool execution |

**Returns:** `dict` - Tool execution result

**Raises:** `ValueError` - If tool not found

##### `search_tools(query: str) -> List[BaseTool]`

Search for tools by name or description.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |

**Returns:** `List[BaseTool]` - List of matching tools

##### `validate_tool_parameters(tool_name: str, parameters: dict) -> bool`

Validate parameters for a tool.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Name of the tool |
| `parameters` | `dict` | Parameters to validate |

**Returns:** `bool` - True if parameters are valid, False otherwise

##### `get_tool_count() -> int`

Get the total number of registered tools.

**Returns:** `int` - Number of registered tools

### BaseTool

Abstract base class for creating custom tools.

#### Class Definition

```python
class BaseTool(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        category: str = "general"
    )
```

#### Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique name of the tool |
| `description` | `str` | Description of what the tool does |
| `category` | `str` | Category of the tool |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Name of the tool |
| `description` | `str` | Description of the tool |
| `category` | `str` | Category of the tool |

#### Abstract Methods

##### `async execute(**kwargs) -> dict`

Execute the tool with given parameters.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `**kwargs` | `Any` | Tool-specific parameters |

**Returns:** `dict` - Tool execution result

**Note:** This method must be implemented by subclasses.

#### Methods

##### `get_parameters_schema() -> dict`

Get the JSON schema for tool parameters.

**Returns:** `dict` - JSON schema describing the tool's parameters

**Example:**
```python
class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="A custom tool example",
            category="custom"
        )
    
    async def execute(self, input_text: str, count: int = 1) -> dict:
        return {
            "result": input_text * count,
            "success": True
        }
```

## Memory

### MemoryManager

Manages persistent storage and retrieval of agent memories.

#### Class Definition

```python
class MemoryManager:
    def __init__(
        self,
        db_path: str = "agent_memory.db",
        embedding_dim: int = 384
    )
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_path` | `str` | `"agent_memory.db"` | Path to SQLite database |
| `embedding_dim` | `int` | `384` | Dimension of embedding vectors |

#### Methods

##### `async store_memory(...) -> str`

Store a new memory.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `str` | Yes | ID of the agent |
| `content` | `str` | Yes | Content of the memory |
| `memory_type` | `str` | Yes | Type of memory |
| `metadata` | `Dict[str, Any]` | No | Additional metadata |
| `importance` | `float` | No | Importance score (0.0-1.0) |

**Returns:** `str` - ID of the stored memory

##### `async retrieve_memories(...) -> List[str]`

Retrieve memories based on criteria.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `str` | No | Filter by agent ID |
| `memory_type` | `str` | No | Filter by memory type |
| `query` | `str` | No | Semantic search query |
| `limit` | `int` | No | Maximum number of memories |
| `importance_threshold` | `float` | No | Minimum importance score |

**Returns:** `List[str]` - List of memory contents

##### `async search_memories(query: str, agent_id: Optional[str] = None, limit: int = 10) -> List[str]`

Search memories using semantic similarity.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Search query |
| `agent_id` | `str` | Optional agent ID filter |
| `limit` | `int` | Maximum results |

**Returns:** `List[str]` - List of matching memory contents

##### `async get_memory_stats(agent_id: Optional[str] = None) -> Dict[str, Any]`

Get memory statistics.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | Optional agent ID filter |

**Returns:** `Dict[str, Any]` - Memory statistics

##### `async delete_memory(memory_id: str) -> bool`

Delete a specific memory.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `memory_id` | `str` | ID of the memory to delete |

**Returns:** `bool` - True if deleted, False if not found

##### `async clear_agent_memories(agent_id: str) -> int`

Clear all memories for an agent.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | `str` | ID of the agent |

**Returns:** `int` - Number of memories deleted

## Data Models

### AgentCapability

Represents a capability that an agent possesses.

```python
class AgentCapability(BaseModel):
    name: str
    description: str
    parameters: Optional[Dict[str, Any]] = None
```

### AgentGoal

Represents a goal for an agent to achieve.

```python
class AgentGoal(BaseModel):
    description: str
    priority: int = 1
    context: Dict[str, Any] = Field(default_factory=dict)
    success_criteria: Optional[str] = None
    max_iterations: int = 10
```

### AgentMessage

Represents a message between agents.

```python
class AgentMessage(BaseModel):
    sender: str
    recipient: str
    content: str
    message_type: str = "text"
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### Task

Represents a high-level task to be executed.

```python
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    priority: int = 1
    assigned_agents: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=lambda: time.time())
    completed_at: Optional[float] = None
    result: Optional[Any] = None
```

### Workflow

Represents a workflow consisting of multiple steps.

```python
class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    steps: List[WorkflowStep]
    context: Dict[str, Any] = Field(default_factory=dict)
```

### WorkflowStep

Represents a step in a workflow.

```python
class WorkflowStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    agent_role: str
    dependencies: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
```

### OllamaResponse

Represents a response from Ollama.

```python
class OllamaResponse(BaseModel):
    content: str
    model: str
    done: bool = True
    tool_calls: List[OllamaToolCall] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### OllamaToolCall

Represents a tool call in an Ollama response.

```python
class OllamaToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    call_id: Optional[str] = None
```

## Enums

### AgentStatus

```python
class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"
```

### TaskStatus

```python
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

---

This API reference provides comprehensive documentation for all public classes and methods in the Ollama Agentic Framework. For more detailed examples and usage patterns, see the [Usage Guide](usage_guide.md) and [Examples](../examples/).

