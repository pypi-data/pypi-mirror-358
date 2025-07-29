"""
Simple Research Agent Example

This example demonstrates how to create a basic research agent using the
Ollama Agentic Framework. The agent can search for information and summarize findings.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent import Agent, AgentGoal, AgentCapability
from core.orchestrator import AgentOrchestrator
from integration.ollama_client import OllamaIntegrationLayer
from tools.tool_registry import ToolRegistry
from memory.memory_manager import MemoryManager


class MockOllamaIntegrationLayer(OllamaIntegrationLayer):
    """Mock Ollama integration for demonstration purposes."""
    
    async def initialize(self) -> bool:
        """Mock initialization."""
        self._available_models = ["llama3.1", "mistral"]
        return True
    
    async def generate_response(self, prompt: str, **kwargs):
        """Mock response generation."""
        from integration.ollama_client import OllamaResponse, OllamaToolCall
        
        # Simple mock responses based on prompt content
        if "search" in prompt.lower() or "research" in prompt.lower():
            # Simulate a tool call for web search
            tool_call = OllamaToolCall(
                name="web_search",
                arguments={"query": "artificial intelligence trends", "max_results": 3}
            )
            return OllamaResponse(
                content="I'll search for information about artificial intelligence trends.",
                tool_calls=[tool_call],
                model="llama3.1"
            )
        elif "summarize" in prompt.lower():
            return OllamaResponse(
                content="""Based on my research, here are the key AI trends:

1. **Large Language Models (LLMs)**: Continued advancement in model capabilities and efficiency
2. **Multimodal AI**: Integration of text, image, and audio processing
3. **AI Agents**: Autonomous systems that can perform complex tasks
4. **Edge AI**: Running AI models on local devices for privacy and speed
5. **AI Safety**: Increased focus on responsible AI development

These trends indicate a move towards more capable, accessible, and safe AI systems.

GOAL_COMPLETED""",
                model="llama3.1"
            )
        else:
            return OllamaResponse(
                content="I understand. Let me work on this step by step.",
                model="llama3.1"
            )


async def main():
    """Main function to demonstrate the research agent."""
    print("🔬 Simple Research Agent Example")
    print("=" * 50)
    
    # Initialize components
    print("Initializing framework components...")
    
    # Use mock Ollama integration for demonstration
    ollama_integration = MockOllamaIntegrationLayer()
    await ollama_integration.initialize()
    
    tool_registry = ToolRegistry()
    memory_manager = MemoryManager(db_path=":memory:")  # Use in-memory database
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(
        ollama_integration=ollama_integration,
        tool_registry=tool_registry,
        memory_manager=memory_manager
    )
    
    # Define research capabilities
    research_capabilities = [
        AgentCapability(
            name="web_search",
            description="Search the web for information on various topics"
        ),
        AgentCapability(
            name="information_synthesis",
            description="Analyze and synthesize information from multiple sources"
        ),
        AgentCapability(
            name="report_generation",
            description="Generate comprehensive reports based on research findings"
        )
    ]
    
    # Create research agent
    research_agent = orchestrator.register_agent(
        agent_id="researcher_001",
        role="Research Specialist",
        description="An AI agent specialized in conducting research and generating insights",
        capabilities=research_capabilities,
        system_prompt="""You are a research specialist AI agent. Your role is to:
1. Search for relevant information on given topics
2. Analyze and synthesize findings from multiple sources
3. Generate clear, comprehensive summaries
4. Provide actionable insights

Always be thorough, accurate, and cite your sources when possible."""
    )
    
    print(f"✅ Created research agent: {research_agent.agent_id}")
    
    # Start the orchestrator
    await orchestrator.start()
    
    # Create a research task
    print("\n📋 Creating research task...")
    task_id = await orchestrator.create_task(
        description="Research current trends in artificial intelligence and provide a comprehensive summary",
        priority=5,
        context={
            "topic": "artificial intelligence trends",
            "focus_areas": ["machine learning", "natural language processing", "computer vision"],
            "output_format": "executive summary"
        }
    )
    
    print(f"✅ Created task: {task_id}")
    
    # Assign task to research agent
    print("\n🎯 Assigning task to research agent...")
    success = await orchestrator.assign_task_to_agent(task_id, research_agent.agent_id)
    
    if success:
        print("✅ Task assigned successfully")
        
        # Monitor agent status
        print("\n🔄 Monitoring agent execution...")
        
        # Wait for task completion (with timeout)
        max_wait_time = 30  # seconds
        wait_time = 0
        
        while wait_time < max_wait_time:
            task = orchestrator.get_task(task_id)
            agent_status = research_agent.get_status()
            
            print(f"⏱️  Time: {wait_time}s | Task: {task.status.value} | Agent: {agent_status.value}")
            
            if task.status.value in ["completed", "failed"]:
                break
            
            await asyncio.sleep(2)
            wait_time += 2
        
        # Get final results
        final_task = orchestrator.get_task(task_id)
        print(f"\n📊 Final task status: {final_task.status.value}")
        
        if final_task.status.value == "completed":
            print("🎉 Research completed successfully!")
            
            # Get agent's memory to see the research process
            print("\n📝 Research Process Summary:")
            memories = await memory_manager.retrieve_memories(
                agent_id=research_agent.agent_id,
                limit=10
            )
            
            for i, memory in enumerate(memories, 1):
                print(f"{i}. {memory}")
        else:
            print("❌ Research task failed or timed out")
    
    else:
        print("❌ Failed to assign task to agent")
    
    # Stop the orchestrator
    await orchestrator.stop()
    
    # Get final statistics
    print("\n📈 Final Statistics:")
    agent_stats = orchestrator.get_agent_status_summary()
    task_stats = orchestrator.get_task_status_summary()
    memory_stats = await memory_manager.get_memory_stats()
    
    print(f"Agent statuses: {agent_stats}")
    print(f"Task statuses: {task_stats}")
    print(f"Memory entries: {memory_stats['total_memories']}")
    
    print("\n✨ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())

