"""
Multi-Agent Collaboration Example

This example demonstrates how multiple agents can work together to solve
a complex problem. We'll create a team of agents that collaborate to
write a technical blog post.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent import Agent, AgentGoal, AgentCapability
from core.orchestrator import AgentOrchestrator, Workflow, WorkflowStep
from integration.ollama_client import OllamaIntegrationLayer, OllamaResponse, OllamaToolCall
from tools.tool_registry import ToolRegistry
from memory.memory_manager import MemoryManager


class MockOllamaIntegrationLayer(OllamaIntegrationLayer):
    """Mock Ollama integration for demonstration purposes."""
    
    def __init__(self):
        super().__init__()
        self.response_count = 0
    
    async def initialize(self) -> bool:
        """Mock initialization."""
        self._available_models = ["llama3.1", "mistral"]
        return True
    
    async def generate_response(self, prompt: str, **kwargs):
        """Mock response generation based on agent role and task."""
        self.response_count += 1
        
        # Determine agent role from system prompt
        system_prompt = kwargs.get("system_prompt", "")
        
        if "Research Specialist" in system_prompt:
            return await self._research_agent_response(prompt)
        elif "Content Writer" in system_prompt:
            return await self._writer_agent_response(prompt)
        elif "Technical Reviewer" in system_prompt:
            return await self._reviewer_agent_response(prompt)
        else:
            return OllamaResponse(
                content="I understand the task and will work on it.",
                model="llama3.1"
            )
    
    async def _research_agent_response(self, prompt: str):
        """Mock responses for research agent."""
        if "research" in prompt.lower() or self.response_count == 1:
            tool_call = OllamaToolCall(
                name="web_search",
                arguments={"query": "microservices architecture best practices", "max_results": 5}
            )
            return OllamaResponse(
                content="I'll research microservices architecture for the blog post.",
                tool_calls=[tool_call],
                model="llama3.1"
            )
        else:
            return OllamaResponse(
                content="""Research completed! Here are the key findings about microservices:

**Key Benefits:**
- Scalability and flexibility
- Technology diversity
- Fault isolation
- Independent deployment

**Best Practices:**
- Domain-driven design
- API-first approach
- Comprehensive monitoring
- Automated testing

**Common Challenges:**
- Distributed system complexity
- Data consistency
- Network latency
- Service discovery

This research provides a solid foundation for the blog post.

GOAL_COMPLETED""",
                model="llama3.1"
            )
    
    async def _writer_agent_response(self, prompt: str):
        """Mock responses for writer agent."""
        if "write" in prompt.lower() or "blog" in prompt.lower():
            return OllamaResponse(
                content="""I'll create a comprehensive blog post based on the research findings.

# Microservices Architecture: A Comprehensive Guide

## Introduction
Microservices architecture has revolutionized how we build and deploy applications...

## Key Benefits
### 1. Scalability and Flexibility
Microservices allow teams to scale individual components based on demand...

### 2. Technology Diversity
Each service can use the most appropriate technology stack...

### 3. Fault Isolation
If one service fails, it doesn't bring down the entire system...

## Best Practices
### Domain-Driven Design
Organize services around business capabilities...

### API-First Approach
Design APIs before implementation...

## Challenges and Solutions
### Distributed System Complexity
Use service mesh and proper monitoring...

## Conclusion
Microservices offer significant benefits but require careful planning...

Blog post draft completed and ready for review!

GOAL_COMPLETED""",
                model="llama3.1"
            )
        else:
            return OllamaResponse(
                content="I'm working on the blog post based on the research provided.",
                model="llama3.1"
            )
    
    async def _reviewer_agent_response(self, prompt: str):
        """Mock responses for reviewer agent."""
        return OllamaResponse(
            content="""Review completed! Here's my feedback on the blog post:

**Strengths:**
✅ Clear structure and logical flow
✅ Comprehensive coverage of key topics
✅ Good balance of benefits and challenges
✅ Practical best practices included

**Suggestions for Improvement:**
📝 Add more specific code examples
📝 Include performance metrics and case studies
📝 Expand on monitoring and observability
📝 Add section on migration strategies

**Technical Accuracy:**
✅ All technical concepts are accurate
✅ Best practices align with industry standards
✅ Challenges are realistically presented

**Overall Assessment:**
The blog post is well-written and technically sound. With the suggested improvements, it will be an excellent resource for developers.

**Recommendation:** Approve with minor revisions

GOAL_COMPLETED""",
            model="llama3.1"
        )


async def main():
    """Main function to demonstrate multi-agent collaboration."""
    print("🤝 Multi-Agent Collaboration Example")
    print("=" * 50)
    
    # Initialize components
    print("Initializing framework components...")
    
    ollama_integration = MockOllamaIntegrationLayer()
    await ollama_integration.initialize()
    
    tool_registry = ToolRegistry()
    memory_manager = MemoryManager(db_path=":memory:")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(
        ollama_integration=ollama_integration,
        tool_registry=tool_registry,
        memory_manager=memory_manager
    )
    
    # Create research agent
    research_agent = orchestrator.register_agent(
        agent_id="researcher_001",
        role="Research Specialist",
        description="Conducts thorough research on technical topics",
        capabilities=[
            AgentCapability(name="web_search", description="Search for information"),
            AgentCapability(name="data_analysis", description="Analyze research data")
        ],
        system_prompt="""You are a Research Specialist AI agent. Your role is to:
1. Conduct comprehensive research on assigned topics
2. Gather information from multiple sources
3. Analyze and synthesize findings
4. Provide structured research summaries

Focus on accuracy, completeness, and relevance."""
    )
    
    # Create writer agent
    writer_agent = orchestrator.register_agent(
        agent_id="writer_001",
        role="Content Writer",
        description="Creates engaging and informative content",
        capabilities=[
            AgentCapability(name="content_creation", description="Write articles and blog posts"),
            AgentCapability(name="technical_writing", description="Explain complex technical concepts")
        ],
        system_prompt="""You are a Content Writer AI agent. Your role is to:
1. Create engaging and informative content
2. Transform research into readable articles
3. Maintain consistent tone and style
4. Structure content for maximum impact

Write for a technical audience but keep content accessible."""
    )
    
    # Create reviewer agent
    reviewer_agent = orchestrator.register_agent(
        agent_id="reviewer_001",
        role="Technical Reviewer",
        description="Reviews content for accuracy and quality",
        capabilities=[
            AgentCapability(name="content_review", description="Review and critique content"),
            AgentCapability(name="technical_validation", description="Validate technical accuracy")
        ],
        system_prompt="""You are a Technical Reviewer AI agent. Your role is to:
1. Review content for technical accuracy
2. Assess clarity and readability
3. Provide constructive feedback
4. Ensure content meets quality standards

Be thorough but constructive in your reviews."""
    )
    
    print(f"✅ Created {len(orchestrator.get_all_agents())} agents")
    
    # Start the orchestrator
    await orchestrator.start()
    
    # Create workflow for blog post creation
    print("\n📋 Creating blog post workflow...")
    
    workflow = Workflow(
        name="Blog Post Creation",
        description="Collaborative workflow to create a technical blog post",
        steps=[
            WorkflowStep(
                id="research_step",
                description="Research microservices architecture and gather key information",
                agent_role="Research Specialist",
                dependencies=[],
                context={"topic": "microservices architecture", "depth": "comprehensive"}
            ),
            WorkflowStep(
                id="writing_step",
                description="Write a blog post based on research findings",
                agent_role="Content Writer",
                dependencies=["research_step"],
                context={"format": "blog post", "audience": "developers", "length": "medium"}
            ),
            WorkflowStep(
                id="review_step",
                description="Review the blog post for accuracy and quality",
                agent_role="Technical Reviewer",
                dependencies=["writing_step"],
                context={"review_type": "technical", "focus": "accuracy and clarity"}
            )
        ],
        context={"project": "microservices blog post", "deadline": "today"}
    )
    
    # Execute workflow
    print("🚀 Starting workflow execution...")
    success = await orchestrator.execute_workflow(workflow)
    
    if success:
        print("✅ Workflow started successfully")
        
        # Monitor workflow progress
        print("\n🔄 Monitoring workflow progress...")
        
        max_wait_time = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait_time:
            # Check agent statuses
            agent_statuses = {}
            for agent in orchestrator.get_all_agents():
                agent_statuses[agent.role] = agent.get_status().value
            
            print(f"⏱️  Time: {wait_time}s | Agent statuses: {agent_statuses}")
            
            # Check if all agents are idle (workflow complete)
            if all(status in ["idle", "completed"] for status in agent_statuses.values()):
                break
            
            await asyncio.sleep(3)
            wait_time += 3
        
        print("\n🎉 Workflow execution completed!")
        
        # Get collaboration results
        print("\n📝 Collaboration Results:")
        
        # Get memories from each agent
        for agent in orchestrator.get_all_agents():
            print(f"\n{agent.role} ({agent.agent_id}):")
            memories = await memory_manager.retrieve_memories(
                agent_id=agent.agent_id,
                limit=3
            )
            for i, memory in enumerate(memories, 1):
                print(f"  {i}. {memory[:100]}...")
        
        # Demonstrate inter-agent communication
        print("\n💬 Demonstrating inter-agent communication...")
        
        # Writer sends message to reviewer
        await orchestrator.send_message(
            sender_id=writer_agent.agent_id,
            recipient_id=reviewer_agent.agent_id,
            content="The blog post draft is ready for your review. Please focus on technical accuracy and readability.",
            message_type="collaboration"
        )
        
        # Reviewer responds
        await orchestrator.send_message(
            sender_id=reviewer_agent.agent_id,
            recipient_id=writer_agent.agent_id,
            content="Thank you! I'll review the post and provide detailed feedback within the hour.",
            message_type="collaboration"
        )
        
        print("✅ Messages exchanged between agents")
        
    else:
        print("❌ Failed to start workflow")
    
    # Stop the orchestrator
    await orchestrator.stop()
    
    # Final statistics
    print("\n📈 Final Statistics:")
    agent_stats = orchestrator.get_agent_status_summary()
    task_stats = orchestrator.get_task_status_summary()
    memory_stats = await memory_manager.get_memory_stats()
    
    print(f"Agent statuses: {agent_stats}")
    print(f"Task statuses: {task_stats}")
    print(f"Total memories: {memory_stats['total_memories']}")
    print(f"Memories by type: {memory_stats['memories_by_type']}")
    
    print("\n✨ Multi-agent collaboration example completed!")


if __name__ == "__main__":
    asyncio.run(main())

