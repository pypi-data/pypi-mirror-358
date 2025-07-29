# Usage Guide

This guide provides practical tutorials and examples for using the EdgeBrain framework effectively. Whether you're building your first agent or creating complex multi-agent systems, this guide will help you understand the framework's capabilities and best practices.

## Table of Contents

- [Getting Started](#getting-started)
- [Creating Your First Agent](#creating-your-first-agent)
- [Working with Tools](#working-with-tools)
- [Memory and Learning](#memory-and-learning)
- [Multi-Agent Collaboration](#multi-agent-collaboration)
- [Workflows and Orchestration](#workflows-and-orchestration)
- [Advanced Patterns](#advanced-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Basic Framework Setup

Before creating agents, you need to set up the core framework components:

```python
import asyncio
from src.core.orchestrator import AgentOrchestrator
from src.integration.ollama_client import OllamaIntegrationLayer
from src.tools.tool_registry import ToolRegistry
from src.memory.memory_manager import MemoryManager

async def setup_framework():
    # Initialize Ollama integration
    ollama_integration = OllamaIntegrationLayer(
        base_url="http://localhost:11434",
        default_model="llama3.1"
    )
    
    # Check if Ollama is available
    if not await ollama_integration.initialize():
        raise RuntimeError("Failed to connect to Ollama. Ensure Ollama is running.")
    
    # Initialize tool registry with default tools
    tool_registry = ToolRegistry()
    
    # Initialize memory manager
    memory_manager = MemoryManager(db_path="agent_memory.db")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(
        ollama_integration=ollama_integration,
        tool_registry=tool_registry,
        memory_manager=memory_manager
    )
    
    return orchestrator

# Usage
orchestrator = await setup_framework()
```

### Environment Configuration

Create a configuration file for your project:

```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class FrameworkConfig:
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.1"
    memory_db_path: str = "agent_memory.db"
    log_level: str = "INFO"
    max_concurrent_agents: int = 5
    task_timeout: int = 300  # 5 minutes
    
    @classmethod
    def from_env(cls) -> 'FrameworkConfig':
        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", cls.ollama_base_url),
            default_model=os.getenv("DEFAULT_MODEL", cls.default_model),
            memory_db_path=os.getenv("MEMORY_DB_PATH", cls.memory_db_path),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            max_concurrent_agents=int(os.getenv("MAX_CONCURRENT_AGENTS", cls.max_concurrent_agents)),
            task_timeout=int(os.getenv("TASK_TIMEOUT", cls.task_timeout))
        )

# Load configuration
config = FrameworkConfig.from_env()
```

## Creating Your First Agent

### Simple Agent Example

Let's create a basic research agent:

```python
from src.core.agent import AgentCapability

async def create_research_agent(orchestrator):
    # Define agent capabilities
    capabilities = [
        AgentCapability(
            name="web_search",
            description="Search the web for information on various topics"
        ),
        AgentCapability(
            name="data_analysis",
            description="Analyze and synthesize information from multiple sources"
        ),
        AgentCapability(
            name="report_writing",
            description="Generate comprehensive reports based on research"
        )
    ]
    
    # Create the agent
    agent = orchestrator.register_agent(
        agent_id="research_agent_001",
        role="Research Specialist",
        description="An AI agent specialized in conducting thorough research and analysis",
        model="llama3.1",
        capabilities=capabilities,
        system_prompt="""You are a research specialist AI agent. Your role is to:
        1. Conduct comprehensive research on assigned topics
        2. Analyze information from multiple sources
        3. Synthesize findings into clear, actionable insights
        4. Generate well-structured reports
        
        Always be thorough, accurate, and cite your sources when possible.
        Focus on providing valuable insights and actionable recommendations."""
    )
    
    return agent

# Usage
research_agent = await create_research_agent(orchestrator)
print(f"Created agent: {research_agent.agent_id} with role: {research_agent.role}")
```

### Assigning Tasks to Agents

Once you have an agent, you can assign tasks:

```python
async def assign_research_task(orchestrator, agent):
    # Create a research task
    task_id = await orchestrator.create_task(
        description="Research the current state of artificial intelligence in healthcare",
        priority=7,
        context={
            "domain": "healthcare",
            "focus_areas": ["diagnosis", "treatment", "drug discovery"],
            "output_format": "executive summary",
            "target_audience": "healthcare executives"
        }
    )
    
    # Assign task to the agent
    success = await orchestrator.assign_task_to_agent(task_id, agent.agent_id)
    
    if success:
        print(f"Task {task_id} assigned successfully to {agent.role}")
        return task_id
    else:
        print("Failed to assign task")
        return None

# Usage
await orchestrator.start()
task_id = await assign_research_task(orchestrator, research_agent)
```

### Monitoring Task Execution

Monitor the progress of your tasks:

```python
async def monitor_task_execution(orchestrator, task_id, timeout=300):
    """Monitor task execution with timeout."""
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        task = orchestrator.get_task(task_id)
        
        if task:
            print(f"Task status: {task.status.value}")
            
            if task.status.value in ["completed", "failed", "cancelled"]:
                return task
        
        await asyncio.sleep(2)
    
    print("Task monitoring timed out")
    return None

# Usage
final_task = await monitor_task_execution(orchestrator, task_id)

if final_task and final_task.status.value == "completed":
    print("Task completed successfully!")
    print(f"Result: {final_task.result}")
else:
    print("Task did not complete successfully")
```

## Working with Tools

### Using Built-in Tools

The framework comes with several built-in tools:

```python
# Get available tools
tools = orchestrator.tool_registry.get_all_tools()
for tool in tools:
    print(f"Tool: {tool.name} - {tool.description}")

# Execute a tool directly
result = await orchestrator.tool_registry.execute_tool(
    "calculator",
    {"expression": "2 + 2 * 3"}
)
print(f"Calculator result: {result}")

# Search for tools
search_tools = orchestrator.tool_registry.search_tools("file")
print(f"File-related tools: {[tool.name for tool in search_tools]}")
```

### Creating Custom Tools

Create your own tools to extend agent capabilities:

```python
from src.tools.tool_registry import BaseTool
import aiohttp
import json

class WeatherTool(BaseTool):
    """Tool for getting weather information."""
    
    def __init__(self, api_key: str):
        super().__init__(
            name="weather_lookup",
            description="Get current weather information for a location",
            category="information"
        )
        self.api_key = api_key
    
    async def execute(self, location: str, units: str = "metric") -> dict:
        """Get weather for a location."""
        try:
            # Mock weather API call (replace with real API)
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "location": location,
                            "temperature": data["main"]["temp"],
                            "description": data["weather"][0]["description"],
                            "humidity": data["main"]["humidity"],
                            "units": units
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API request failed with status {response.status}"
                        }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Register the custom tool
weather_tool = WeatherTool(api_key="your_api_key_here")
orchestrator.tool_registry.register_tool(weather_tool)

# Test the tool
weather_result = await orchestrator.tool_registry.execute_tool(
    "weather_lookup",
    {"location": "New York", "units": "imperial"}
)
print(f"Weather result: {weather_result}")
```

### Tool Categories and Organization

Organize tools by category for better management:

```python
# Get tools by category
information_tools = orchestrator.tool_registry.get_tools_by_category("information")
utility_tools = orchestrator.tool_registry.get_tools_by_category("utility")

print(f"Information tools: {[tool.name for tool in information_tools]}")
print(f"Utility tools: {[tool.name for tool in utility_tools]}")

# Get all categories
categories = orchestrator.tool_registry.get_categories()
print(f"Available categories: {categories}")
```

## Memory and Learning

### Storing and Retrieving Memories

Agents can store and retrieve memories for learning and context:

```python
async def demonstrate_memory_usage(orchestrator, agent_id):
    memory_manager = orchestrator.memory_manager
    
    # Store different types of memories
    memories = [
        {
            "content": "Successfully completed research on AI in healthcare",
            "memory_type": "achievement",
            "importance": 0.8
        },
        {
            "content": "User prefers executive summaries over detailed reports",
            "memory_type": "preference",
            "importance": 0.9
        },
        {
            "content": "Healthcare domain requires focus on FDA regulations",
            "memory_type": "domain_knowledge",
            "importance": 0.7
        }
    ]
    
    # Store memories
    memory_ids = []
    for memory in memories:
        memory_id = await memory_manager.store_memory(
            agent_id=agent_id,
            content=memory["content"],
            memory_type=memory["memory_type"],
            importance=memory["importance"]
        )
        memory_ids.append(memory_id)
        print(f"Stored memory: {memory_id}")
    
    # Retrieve memories by type
    achievements = await memory_manager.retrieve_memories(
        agent_id=agent_id,
        memory_type="achievement"
    )
    print(f"Achievement memories: {achievements}")
    
    # Search memories semantically
    search_results = await memory_manager.search_memories(
        query="healthcare research",
        agent_id=agent_id,
        limit=5
    )
    print(f"Search results: {search_results}")
    
    # Get memory statistics
    stats = await memory_manager.get_memory_stats(agent_id)
    print(f"Memory stats: {stats}")

# Usage
await demonstrate_memory_usage(orchestrator, research_agent.agent_id)
```

### Memory-Based Learning

Use memories to improve agent performance:

```python
async def create_learning_agent(orchestrator):
    """Create an agent that learns from its experiences."""
    
    learning_agent = orchestrator.register_agent(
        agent_id="learning_agent_001",
        role="Learning Assistant",
        description="An agent that learns and adapts from previous interactions",
        system_prompt="""You are a learning assistant that improves over time.
        Before starting any task, review your previous experiences and learnings.
        After completing tasks, reflect on what worked well and what could be improved.
        Use your memories to provide better assistance in future interactions."""
    )
    
    return learning_agent

async def task_with_learning(orchestrator, agent, task_description):
    """Execute a task with learning integration."""
    
    # Retrieve relevant memories before starting
    relevant_memories = await orchestrator.memory_manager.search_memories(
        query=task_description,
        agent_id=agent.agent_id,
        limit=5
    )
    
    # Create task with memory context
    task_id = await orchestrator.create_task(
        description=task_description,
        context={
            "relevant_memories": relevant_memories,
            "learning_mode": True
        }
    )
    
    # Execute task
    await orchestrator.assign_task_to_agent(task_id, agent.agent_id)
    
    # Wait for completion and store learning
    task = await monitor_task_execution(orchestrator, task_id)
    
    if task and task.status.value == "completed":
        # Store learning from this task
        await orchestrator.memory_manager.store_memory(
            agent_id=agent.agent_id,
            content=f"Completed task: {task_description}. Outcome: {task.result}",
            memory_type="experience",
            importance=0.8
        )
    
    return task

# Usage
learning_agent = await create_learning_agent(orchestrator)
task = await task_with_learning(
    orchestrator,
    learning_agent,
    "Analyze customer feedback and provide improvement recommendations"
)
```

## Multi-Agent Collaboration

### Creating Agent Teams

Build teams of specialized agents:

```python
async def create_content_creation_team(orchestrator):
    """Create a team of agents for content creation."""
    
    # Research Agent
    researcher = orchestrator.register_agent(
        agent_id="researcher_001",
        role="Research Specialist",
        description="Conducts thorough research and gathers information",
        capabilities=[
            AgentCapability(name="web_search", description="Search for information"),
            AgentCapability(name="data_analysis", description="Analyze research data")
        ]
    )
    
    # Writer Agent
    writer = orchestrator.register_agent(
        agent_id="writer_001",
        role="Content Writer",
        description="Creates engaging and informative content",
        capabilities=[
            AgentCapability(name="content_creation", description="Write articles and posts"),
            AgentCapability(name="editing", description="Edit and refine content")
        ]
    )
    
    # Editor Agent
    editor = orchestrator.register_agent(
        agent_id="editor_001",
        role="Content Editor",
        description="Reviews and improves content quality",
        capabilities=[
            AgentCapability(name="content_review", description="Review content quality"),
            AgentCapability(name="fact_checking", description="Verify information accuracy")
        ]
    )
    
    return {
        "researcher": researcher,
        "writer": writer,
        "editor": editor
    }

# Create the team
team = await create_content_creation_team(orchestrator)
print(f"Created team with {len(team)} agents")
```

### Inter-Agent Communication

Enable agents to communicate and collaborate:

```python
async def demonstrate_agent_communication(orchestrator, team):
    """Demonstrate communication between agents."""
    
    researcher = team["researcher"]
    writer = team["writer"]
    editor = team["editor"]
    
    # Researcher sends findings to writer
    await orchestrator.send_message(
        sender_id=researcher.agent_id,
        recipient_id=writer.agent_id,
        content="""Research completed on AI trends in 2024:
        
        Key findings:
        - 40% increase in enterprise AI adoption
        - Focus on responsible AI development
        - Growth in multimodal AI applications
        
        Detailed data and sources are available in shared memory.""",
        message_type="research_findings"
    )
    
    # Writer acknowledges and requests clarification
    await orchestrator.send_message(
        sender_id=writer.agent_id,
        recipient_id=researcher.agent_id,
        content="Thank you for the research! Could you provide more specific statistics on enterprise adoption rates by industry?",
        message_type="clarification_request"
    )
    
    # Broadcast project update
    await orchestrator.broadcast_message(
        sender_id=researcher.agent_id,
        content="Research phase completed. Moving to content creation phase.",
        message_type="project_update"
    )
    
    print("Agent communication demonstrated")

# Usage
await demonstrate_agent_communication(orchestrator, team)
```

### Collaborative Task Execution

Coordinate multiple agents on a single task:

```python
async def collaborative_content_creation(orchestrator, team, topic):
    """Create content collaboratively using multiple agents."""
    
    # Phase 1: Research
    research_task_id = await orchestrator.create_task(
        description=f"Conduct comprehensive research on: {topic}",
        priority=8,
        context={"phase": "research", "topic": topic}
    )
    
    await orchestrator.assign_task_to_agent(research_task_id, team["researcher"].agent_id)
    research_task = await monitor_task_execution(orchestrator, research_task_id)
    
    if research_task.status.value != "completed":
        print("Research phase failed")
        return None
    
    # Phase 2: Writing
    writing_task_id = await orchestrator.create_task(
        description=f"Write an article about: {topic}",
        priority=7,
        context={
            "phase": "writing",
            "topic": topic,
            "research_results": research_task.result
        }
    )
    
    await orchestrator.assign_task_to_agent(writing_task_id, team["writer"].agent_id)
    writing_task = await monitor_task_execution(orchestrator, writing_task_id)
    
    if writing_task.status.value != "completed":
        print("Writing phase failed")
        return None
    
    # Phase 3: Editing
    editing_task_id = await orchestrator.create_task(
        description=f"Review and edit the article about: {topic}",
        priority=6,
        context={
            "phase": "editing",
            "topic": topic,
            "draft_content": writing_task.result
        }
    )
    
    await orchestrator.assign_task_to_agent(editing_task_id, team["editor"].agent_id)
    editing_task = await monitor_task_execution(orchestrator, editing_task_id)
    
    return editing_task

# Usage
final_article = await collaborative_content_creation(
    orchestrator,
    team,
    "The Future of Artificial Intelligence in Business"
)

if final_article and final_article.status.value == "completed":
    print("Article creation completed successfully!")
    print(f"Final article: {final_article.result}")
```

## Workflows and Orchestration

### Creating Workflows

Define complex multi-step workflows:

```python
from src.core.orchestrator import Workflow, WorkflowStep

async def create_product_launch_workflow():
    """Create a workflow for product launch preparation."""
    
    workflow = Workflow(
        name="Product Launch Preparation",
        description="Comprehensive workflow for preparing a product launch",
        steps=[
            WorkflowStep(
                id="market_research",
                description="Conduct market research and competitive analysis",
                agent_role="Research Specialist",
                dependencies=[],
                context={"research_scope": "comprehensive", "timeline": "2_weeks"}
            ),
            WorkflowStep(
                id="content_strategy",
                description="Develop content strategy and messaging",
                agent_role="Content Strategist",
                dependencies=["market_research"],
                context={"content_types": ["blog", "social", "email"], "tone": "professional"}
            ),
            WorkflowStep(
                id="content_creation",
                description="Create marketing content and materials",
                agent_role="Content Writer",
                dependencies=["content_strategy"],
                context={"deliverables": ["landing_page", "blog_posts", "social_content"]}
            ),
            WorkflowStep(
                id="design_review",
                description="Review and approve all content and designs",
                agent_role="Design Reviewer",
                dependencies=["content_creation"],
                context={"review_criteria": ["brand_consistency", "message_clarity", "visual_appeal"]}
            ),
            WorkflowStep(
                id="launch_coordination",
                description="Coordinate launch activities and timeline",
                agent_role="Project Manager",
                dependencies=["design_review"],
                context={"launch_channels": ["website", "social_media", "email"], "go_live_date": "2024-02-01"}
            )
        ],
        context={
            "product_name": "AI Assistant Pro",
            "target_audience": "business_professionals",
            "budget": "$50000",
            "timeline": "6_weeks"
        }
    )
    
    return workflow

async def execute_workflow_with_monitoring(orchestrator, workflow):
    """Execute a workflow with detailed monitoring."""
    
    print(f"Starting workflow: {workflow.name}")
    
    # Execute workflow
    success = await orchestrator.execute_workflow(workflow)
    
    if not success:
        print("Failed to start workflow")
        return False
    
    # Monitor workflow progress
    completed_steps = set()
    total_steps = len(workflow.steps)
    
    while len(completed_steps) < total_steps:
        # Check agent statuses
        agent_statuses = {}
        for agent in orchestrator.get_all_agents():
            status = agent.get_status()
            agent_statuses[agent.role] = status.value
        
        print(f"Workflow progress: {len(completed_steps)}/{total_steps} steps completed")
        print(f"Agent statuses: {agent_statuses}")
        
        # Simulate step completion check
        # In a real implementation, you'd track actual step completion
        await asyncio.sleep(5)
        
        # For demo purposes, assume steps complete over time
        if len(completed_steps) < total_steps:
            completed_steps.add(workflow.steps[len(completed_steps)].id)
    
    print("Workflow completed successfully!")
    return True

# Usage
workflow = await create_product_launch_workflow()
await execute_workflow_with_monitoring(orchestrator, workflow)
```

### Conditional Workflows

Create workflows with conditional logic:

```python
async def create_conditional_workflow(orchestrator, content_type):
    """Create a workflow that adapts based on content type."""
    
    base_steps = [
        WorkflowStep(
            id="content_planning",
            description="Plan content structure and approach",
            agent_role="Content Strategist",
            dependencies=[],
            context={"content_type": content_type}
        )
    ]
    
    # Add conditional steps based on content type
    if content_type == "technical_article":
        base_steps.extend([
            WorkflowStep(
                id="technical_research",
                description="Conduct technical research and validation",
                agent_role="Technical Researcher",
                dependencies=["content_planning"],
                context={"depth": "expert_level", "accuracy_required": True}
            ),
            WorkflowStep(
                id="technical_writing",
                description="Write technical content with code examples",
                agent_role="Technical Writer",
                dependencies=["technical_research"],
                context={"include_code": True, "target_audience": "developers"}
            )
        ])
    elif content_type == "marketing_copy":
        base_steps.extend([
            WorkflowStep(
                id="market_analysis",
                description="Analyze target market and messaging",
                agent_role="Marketing Analyst",
                dependencies=["content_planning"],
                context={"focus": "conversion_optimization"}
            ),
            WorkflowStep(
                id="copywriting",
                description="Create persuasive marketing copy",
                agent_role="Copywriter",
                dependencies=["market_analysis"],
                context={"tone": "persuasive", "cta_required": True}
            )
        ])
    
    # Common final step
    base_steps.append(
        WorkflowStep(
            id="final_review",
            description="Final review and approval",
            agent_role="Content Editor",
            dependencies=[step.id for step in base_steps[-1:]],  # Depends on last content step
            context={"review_type": "comprehensive"}
        )
    )
    
    workflow = Workflow(
        name=f"{content_type.title()} Creation Workflow",
        description=f"Adaptive workflow for creating {content_type}",
        steps=base_steps,
        context={"content_type": content_type, "adaptive": True}
    )
    
    return workflow

# Usage
technical_workflow = await create_conditional_workflow(orchestrator, "technical_article")
marketing_workflow = await create_conditional_workflow(orchestrator, "marketing_copy")
```

## Advanced Patterns

### Agent Specialization

Create highly specialized agents for specific domains:

```python
async def create_specialized_agents(orchestrator):
    """Create domain-specific specialized agents."""
    
    # Financial Analysis Agent
    financial_agent = orchestrator.register_agent(
        agent_id="financial_analyst_001",
        role="Financial Analyst",
        description="Specialized in financial analysis and market research",
        model="llama3.1",
        capabilities=[
            AgentCapability(name="financial_modeling", description="Create financial models"),
            AgentCapability(name="market_analysis", description="Analyze market trends"),
            AgentCapability(name="risk_assessment", description="Assess investment risks")
        ],
        system_prompt="""You are a financial analyst AI with expertise in:
        - Financial modeling and forecasting
        - Market analysis and trend identification
        - Risk assessment and portfolio optimization
        - Regulatory compliance and reporting
        
        Always provide data-driven insights with proper risk disclaimers."""
    )
    
    # Legal Research Agent
    legal_agent = orchestrator.register_agent(
        agent_id="legal_researcher_001",
        role="Legal Researcher",
        description="Specialized in legal research and compliance analysis",
        model="llama3.1",
        capabilities=[
            AgentCapability(name="legal_research", description="Research legal precedents"),
            AgentCapability(name="compliance_analysis", description="Analyze regulatory compliance"),
            AgentCapability(name="contract_review", description="Review contract terms")
        ],
        system_prompt="""You are a legal research AI specialized in:
        - Legal precedent research and case law analysis
        - Regulatory compliance and policy interpretation
        - Contract analysis and risk identification
        - Legal document drafting assistance
        
        Always include appropriate legal disclaimers and recommend consulting qualified attorneys."""
    )
    
    # Technical Architecture Agent
    tech_agent = orchestrator.register_agent(
        agent_id="tech_architect_001",
        role="Technical Architect",
        description="Specialized in software architecture and system design",
        model="codellama",  # Use code-specialized model
        capabilities=[
            AgentCapability(name="system_design", description="Design software architectures"),
            AgentCapability(name="code_review", description="Review code quality and patterns"),
            AgentCapability(name="performance_optimization", description="Optimize system performance")
        ],
        system_prompt="""You are a technical architect AI with expertise in:
        - Software architecture design and patterns
        - System scalability and performance optimization
        - Code quality assessment and best practices
        - Technology stack evaluation and selection
        
        Focus on maintainable, scalable, and secure solutions."""
    )
    
    return {
        "financial": financial_agent,
        "legal": legal_agent,
        "technical": tech_agent
    }

# Usage
specialized_agents = await create_specialized_agents(orchestrator)
```

### Dynamic Agent Creation

Create agents dynamically based on requirements:

```python
async def create_agent_factory(orchestrator):
    """Factory for creating agents based on specifications."""
    
    agent_templates = {
        "researcher": {
            "role": "Research Specialist",
            "description": "Conducts research and analysis",
            "capabilities": ["web_search", "data_analysis", "report_writing"],
            "model": "llama3.1"
        },
        "writer": {
            "role": "Content Writer",
            "description": "Creates written content",
            "capabilities": ["content_creation", "editing", "seo_optimization"],
            "model": "llama3.1"
        },
        "analyst": {
            "role": "Data Analyst",
            "description": "Analyzes data and generates insights",
            "capabilities": ["statistical_analysis", "data_visualization", "predictive_modeling"],
            "model": "llama3.1"
        },
        "coder": {
            "role": "Software Developer",
            "description": "Develops and maintains software",
            "capabilities": ["programming", "debugging", "code_review"],
            "model": "codellama"
        }
    }
    
    async def create_agent(agent_type: str, agent_id: str, specialization: str = None):
        """Create an agent of the specified type."""
        
        if agent_type not in agent_templates:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        template = agent_templates[agent_type]
        
        # Customize based on specialization
        if specialization:
            description = f"{template['description']} specialized in {specialization}"
            system_prompt = f"You are a {template['role']} specialized in {specialization}."
        else:
            description = template['description']
            system_prompt = f"You are a {template['role']}."
        
        # Create capabilities
        capabilities = [
            AgentCapability(name=cap, description=f"Capability: {cap}")
            for cap in template['capabilities']
        ]
        
        # Register agent
        agent = orchestrator.register_agent(
            agent_id=agent_id,
            role=template['role'],
            description=description,
            model=template['model'],
            capabilities=capabilities,
            system_prompt=system_prompt
        )
        
        return agent
    
    return create_agent

# Usage
agent_factory = await create_agent_factory(orchestrator)

# Create specialized agents
healthcare_researcher = await agent_factory("researcher", "healthcare_researcher_001", "healthcare")
fintech_analyst = await agent_factory("analyst", "fintech_analyst_001", "financial technology")
python_developer = await agent_factory("coder", "python_dev_001", "Python development")
```

### Error Handling and Recovery

Implement robust error handling:

```python
async def robust_task_execution(orchestrator, agent_id, task_description, max_retries=3):
    """Execute a task with error handling and retry logic."""
    
    for attempt in range(max_retries):
        try:
            # Create task
            task_id = await orchestrator.create_task(
                description=task_description,
                context={"attempt": attempt + 1, "max_retries": max_retries}
            )
            
            # Assign to agent
            success = await orchestrator.assign_task_to_agent(task_id, agent_id)
            
            if not success:
                print(f"Attempt {attempt + 1}: Failed to assign task")
                continue
            
            # Monitor execution with timeout
            task = await monitor_task_execution(orchestrator, task_id, timeout=120)
            
            if task and task.status.value == "completed":
                print(f"Task completed successfully on attempt {attempt + 1}")
                return task
            elif task and task.status.value == "failed":
                print(f"Attempt {attempt + 1}: Task failed")
                
                # Store failure information for learning
                await orchestrator.memory_manager.store_memory(
                    agent_id=agent_id,
                    content=f"Task failed: {task_description}. Attempt {attempt + 1}",
                    memory_type="failure",
                    importance=0.7
                )
            else:
                print(f"Attempt {attempt + 1}: Task timed out")
        
        except Exception as e:
            print(f"Attempt {attempt + 1}: Exception occurred: {e}")
        
        # Wait before retry
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    print(f"Task failed after {max_retries} attempts")
    return None

# Usage
result = await robust_task_execution(
    orchestrator,
    research_agent.agent_id,
    "Analyze the impact of AI on job markets"
)
```

## Best Practices

### Performance Optimization

Optimize your agent system for better performance:

```python
# 1. Use appropriate models for different tasks
async def optimize_model_selection(orchestrator):
    """Optimize model selection based on task requirements."""
    
    # Lightweight model for simple tasks
    simple_agent = orchestrator.register_agent(
        agent_id="simple_agent_001",
        role="Simple Assistant",
        description="Handles simple, quick tasks",
        model="phi3"  # Faster, smaller model
    )
    
    # Powerful model for complex reasoning
    complex_agent = orchestrator.register_agent(
        agent_id="complex_agent_001",
        role="Complex Reasoner",
        description="Handles complex reasoning tasks",
        model="llama3.1"  # More capable model
    )
    
    # Code-specialized model for programming tasks
    code_agent = orchestrator.register_agent(
        agent_id="code_agent_001",
        role="Code Specialist",
        description="Handles programming and code-related tasks",
        model="codellama"  # Specialized for code
    )

# 2. Implement caching for repeated operations
class CachedMemoryManager:
    """Memory manager with caching for better performance."""
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_cached_memories(self, agent_id: str, query: str):
        """Get memories with caching."""
        cache_key = f"{agent_id}:{query}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # Fetch from memory manager
        memories = await self.memory_manager.search_memories(query, agent_id)
        
        # Cache the result
        self.cache[cache_key] = (memories, time.time())
        
        return memories

# 3. Batch operations when possible
async def batch_task_creation(orchestrator, task_descriptions):
    """Create multiple tasks efficiently."""
    
    tasks = []
    for description in task_descriptions:
        task_id = await orchestrator.create_task(description)
        tasks.append(task_id)
    
    return tasks

# 4. Use connection pooling for database operations
async def optimize_database_connections():
    """Optimize database connections for better performance."""
    
    # Use connection pooling
    memory_manager = MemoryManager(
        db_path="agent_memory.db",
        pool_size=10,  # Hypothetical parameter
        max_overflow=20
    )
    
    return memory_manager
```

### Security Considerations

Implement security best practices:

```python
# 1. Input validation and sanitization
def validate_task_input(description: str, context: dict) -> bool:
    """Validate task inputs for security."""
    
    # Check for malicious content
    dangerous_patterns = [
        "eval(",
        "exec(",
        "__import__",
        "subprocess",
        "os.system"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in description.lower():
            return False
    
    # Validate context structure
    if not isinstance(context, dict):
        return False
    
    # Check context size
    if len(str(context)) > 10000:  # Limit context size
        return False
    
    return True

# 2. Secure tool execution
class SecureToolRegistry(ToolRegistry):
    """Tool registry with security controls."""
    
    def __init__(self):
        super().__init__()
        self.allowed_tools = set()
        self.sandbox_mode = True
    
    def set_allowed_tools(self, tool_names: list):
        """Set which tools are allowed to execute."""
        self.allowed_tools = set(tool_names)
    
    async def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        """Execute tool with security checks."""
        
        # Check if tool is allowed
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return {
                "success": False,
                "error": f"Tool {tool_name} is not allowed"
            }
        
        # Validate parameters
        if not self.validate_tool_parameters(tool_name, parameters):
            return {
                "success": False,
                "error": "Invalid parameters"
            }
        
        # Execute with timeout
        try:
            return await asyncio.wait_for(
                super().execute_tool(tool_name, parameters),
                timeout=30  # 30 second timeout
            )
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Tool execution timed out"
            }

# 3. Memory access controls
async def secure_memory_access(memory_manager, agent_id: str, requested_agent_id: str):
    """Control memory access between agents."""
    
    # Agents can only access their own memories by default
    if agent_id != requested_agent_id:
        # Check if cross-agent access is allowed
        permissions = await memory_manager.get_agent_permissions(agent_id)
        if "read_other_memories" not in permissions:
            raise PermissionError("Agent not authorized to access other agent memories")
    
    return True
```

### Monitoring and Logging

Implement comprehensive monitoring:

```python
import logging
import time
from typing import Dict, Any

# 1. Set up structured logging
def setup_logging():
    """Set up comprehensive logging for the framework."""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for detailed logs
    file_handler = logging.FileHandler('agent_framework.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    logging.getLogger('src.core.agent').setLevel(logging.INFO)
    logging.getLogger('src.integration.ollama_client').setLevel(logging.WARNING)

# 2. Performance monitoring
class PerformanceMonitor:
    """Monitor performance metrics for the framework."""
    
    def __init__(self):
        self.metrics = {
            "task_completion_times": [],
            "agent_response_times": [],
            "memory_operations": [],
            "tool_executions": []
        }
    
    def record_task_completion(self, task_id: str, duration: float):
        """Record task completion time."""
        self.metrics["task_completion_times"].append({
            "task_id": task_id,
            "duration": duration,
            "timestamp": time.time()
        })
    
    def record_agent_response(self, agent_id: str, duration: float):
        """Record agent response time."""
        self.metrics["agent_response_times"].append({
            "agent_id": agent_id,
            "duration": duration,
            "timestamp": time.time()
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {}
        
        # Task completion times
        if self.metrics["task_completion_times"]:
            times = [m["duration"] for m in self.metrics["task_completion_times"]]
            summary["avg_task_completion_time"] = sum(times) / len(times)
            summary["max_task_completion_time"] = max(times)
            summary["min_task_completion_time"] = min(times)
        
        # Agent response times
        if self.metrics["agent_response_times"]:
            times = [m["duration"] for m in self.metrics["agent_response_times"]]
            summary["avg_agent_response_time"] = sum(times) / len(times)
            summary["max_agent_response_time"] = max(times)
            summary["min_agent_response_time"] = min(times)
        
        return summary

# 3. Health monitoring
async def health_check(orchestrator) -> Dict[str, Any]:
    """Perform comprehensive health check."""
    
    health_status = {
        "timestamp": time.time(),
        "overall_status": "healthy",
        "components": {}
    }
    
    # Check Ollama connection
    try:
        models = orchestrator.ollama_integration.get_available_models()
        health_status["components"]["ollama"] = {
            "status": "healthy",
            "available_models": len(models)
        }
    except Exception as e:
        health_status["components"]["ollama"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Check memory system
    try:
        stats = await orchestrator.memory_manager.get_memory_stats()
        health_status["components"]["memory"] = {
            "status": "healthy",
            "total_memories": stats.get("total_memories", 0)
        }
    except Exception as e:
        health_status["components"]["memory"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "degraded"
    
    # Check agents
    agents = orchestrator.get_all_agents()
    agent_statuses = orchestrator.get_agent_status_summary()
    
    health_status["components"]["agents"] = {
        "status": "healthy",
        "total_agents": len(agents),
        "status_summary": agent_statuses
    }
    
    return health_status

# Usage
setup_logging()
monitor = PerformanceMonitor()

# Regular health checks
async def periodic_health_check(orchestrator, interval=300):
    """Perform periodic health checks."""
    while True:
        health = await health_check(orchestrator)
        logging.info(f"Health check: {health['overall_status']}")
        
        if health["overall_status"] != "healthy":
            logging.warning(f"System health degraded: {health}")
        
        await asyncio.sleep(interval)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Agent Not Responding

**Problem**: Agent appears stuck or not responding to tasks.

**Diagnosis**:
```python
async def diagnose_agent_issues(orchestrator, agent_id):
    """Diagnose common agent issues."""
    
    agent = orchestrator.get_agent(agent_id)
    if not agent:
        return "Agent not found"
    
    status = agent.get_status()
    print(f"Agent status: {status.value}")
    
    # Check recent memories
    recent_memories = await orchestrator.memory_manager.retrieve_memories(
        agent_id=agent_id,
        limit=5
    )
    print(f"Recent memories: {len(recent_memories)}")
    
    # Check assigned tasks
    tasks = orchestrator.get_all_tasks()
    agent_tasks = [t for t in tasks if agent_id in t.assigned_agents]
    print(f"Assigned tasks: {len(agent_tasks)}")
    
    return "Diagnosis complete"
```

**Solutions**:
- Check if Ollama is running and accessible
- Verify the agent's model is available
- Check for memory or resource constraints
- Review recent error logs

#### 2. Memory Issues

**Problem**: High memory usage or slow memory operations.

**Solutions**:
```python
async def optimize_memory_usage(memory_manager):
    """Optimize memory usage."""
    
    # Clean up old memories
    cutoff_date = datetime.now() - timedelta(days=30)
    
    # Get memory statistics
    stats = await memory_manager.get_memory_stats()
    print(f"Total memories before cleanup: {stats['total_memories']}")
    
    # Implement memory cleanup (hypothetical method)
    # await memory_manager.cleanup_old_memories(cutoff_date)
    
    # Optimize database
    # await memory_manager.optimize_database()
    
    print("Memory optimization complete")
```

#### 3. Tool Execution Failures

**Problem**: Tools failing to execute or timing out.

**Solutions**:
```python
async def debug_tool_execution(tool_registry, tool_name, parameters):
    """Debug tool execution issues."""
    
    # Validate tool exists
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        return f"Tool {tool_name} not found"
    
    # Validate parameters
    if not tool_registry.validate_tool_parameters(tool_name, parameters):
        return "Invalid parameters"
    
    # Test execution with timeout
    try:
        result = await asyncio.wait_for(
            tool_registry.execute_tool(tool_name, parameters),
            timeout=10
        )
        return f"Tool executed successfully: {result}"
    except asyncio.TimeoutError:
        return "Tool execution timed out"
    except Exception as e:
        return f"Tool execution failed: {e}"
```

### Performance Tuning

Optimize your system for better performance:

```python
# 1. Model selection optimization
async def optimize_model_usage(orchestrator):
    """Optimize model usage based on task complexity."""
    
    # Use faster models for simple tasks
    simple_tasks = ["summarize", "translate", "format"]
    complex_tasks = ["analyze", "research", "create"]
    
    for agent in orchestrator.get_all_agents():
        # Analyze agent's typical tasks
        memories = await orchestrator.memory_manager.retrieve_memories(
            agent_id=agent.agent_id,
            memory_type="task",
            limit=10
        )
        
        # Determine optimal model based on task history
        if any(task in str(memories).lower() for task in complex_tasks):
            recommended_model = "llama3.1"
        else:
            recommended_model = "phi3"
        
        print(f"Agent {agent.agent_id}: Recommended model {recommended_model}")

# 2. Concurrent execution optimization
async def optimize_concurrent_execution(orchestrator, max_concurrent=3):
    """Optimize concurrent task execution."""
    
    # Limit concurrent agents
    active_agents = [
        agent for agent in orchestrator.get_all_agents()
        if agent.get_status().value in ["thinking", "acting"]
    ]
    
    if len(active_agents) > max_concurrent:
        print(f"Too many active agents ({len(active_agents)}), consider reducing load")
    
    # Implement task queuing
    pending_tasks = [
        task for task in orchestrator.get_all_tasks()
        if task.status.value == "pending"
    ]
    
    print(f"Pending tasks: {len(pending_tasks)}")
    
    # Prioritize tasks
    high_priority_tasks = [
        task for task in pending_tasks
        if task.priority >= 7
    ]
    
    print(f"High priority tasks: {len(high_priority_tasks)}")
```

This comprehensive usage guide provides practical examples and patterns for building effective agent systems with the Ollama Agentic Framework. Use these examples as starting points for your own implementations, and adapt them to your specific use cases and requirements.

