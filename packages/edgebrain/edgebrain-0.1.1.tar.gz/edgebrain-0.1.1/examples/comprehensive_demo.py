"""
Comprehensive Demo Script

This script demonstrates the full capabilities of the Ollama Agentic Framework
by showcasing various features, agent types, and use cases.
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.agent import Agent, AgentGoal, AgentCapability
from core.orchestrator import AgentOrchestrator, Workflow, WorkflowStep
from integration.ollama_client import OllamaIntegrationLayer, OllamaResponse, OllamaToolCall
from tools.tool_registry import ToolRegistry, BaseTool
from memory.memory_manager import MemoryManager


class AdvancedMockOllamaIntegrationLayer(OllamaIntegrationLayer):
    """Advanced mock Ollama integration for comprehensive demonstration."""
    
    def __init__(self):
        super().__init__()
        self.conversation_history = {}
        self.agent_personalities = {
            "Research Specialist": "analytical and thorough",
            "Content Writer": "creative and engaging",
            "Data Analyst": "precise and data-driven",
            "Project Manager": "organized and strategic",
            "Quality Assurance": "detail-oriented and systematic"
        }
    
    async def initialize(self) -> bool:
        """Mock initialization."""
        self._available_models = ["llama3.1", "mistral", "codellama", "phi3"]
        return True
    
    async def generate_response(self, prompt: str, **kwargs):
        """Generate contextual responses based on agent role and task."""
        system_prompt = kwargs.get("system_prompt", "")
        
        # Determine agent role
        agent_role = "General"
        for role in self.agent_personalities:
            if role in system_prompt:
                agent_role = role
                break
        
        # Generate response based on role and prompt content
        if agent_role == "Research Specialist":
            return await self._research_response(prompt)
        elif agent_role == "Content Writer":
            return await self._writer_response(prompt)
        elif agent_role == "Data Analyst":
            return await self._analyst_response(prompt)
        elif agent_role == "Project Manager":
            return await self._manager_response(prompt)
        elif agent_role == "Quality Assurance":
            return await self._qa_response(prompt)
        else:
            return await self._general_response(prompt)
    
    async def _research_response(self, prompt: str):
        """Research specialist responses."""
        if "market analysis" in prompt.lower():
            tool_call = OllamaToolCall(
                name="web_search",
                arguments={"query": "AI market trends 2024", "max_results": 5}
            )
            return OllamaResponse(
                content="I'll conduct a comprehensive market analysis of the AI industry.",
                tool_calls=[tool_call],
                model="llama3.1"
            )
        else:
            return OllamaResponse(
                content="""Research completed! Key findings:

**Market Overview:**
- AI market size: $150B+ in 2024
- Growth rate: 35% CAGR
- Key drivers: Enterprise adoption, cloud computing, edge AI

**Technology Trends:**
- Large Language Models (LLMs) dominating
- Multimodal AI gaining traction
- AI agents and automation expanding

**Investment Patterns:**
- $50B+ in AI investments this year
- Focus on enterprise applications
- Growing interest in AI safety

**Competitive Landscape:**
- OpenAI, Google, Microsoft leading
- Emerging players in specialized niches
- Open-source alternatives gaining ground

GOAL_COMPLETED""",
                model="llama3.1"
            )
    
    async def _writer_response(self, prompt: str):
        """Content writer responses."""
        return OllamaResponse(
            content="""# The Future of AI: Transforming Industries and Society

## Executive Summary
Artificial Intelligence is reshaping our world at an unprecedented pace...

## Introduction
In 2024, we stand at the threshold of an AI revolution that promises to transform every aspect of human society...

## Current State of AI
### Technological Breakthroughs
- **Large Language Models**: GPT-4, Claude, and Llama have demonstrated remarkable capabilities
- **Multimodal AI**: Systems that understand text, images, and audio simultaneously
- **AI Agents**: Autonomous systems capable of complex reasoning and action

### Market Dynamics
The AI market has experienced explosive growth, with investments reaching record highs...

## Industry Applications
### Healthcare
AI is revolutionizing diagnosis, drug discovery, and personalized treatment...

### Finance
From algorithmic trading to fraud detection, AI is transforming financial services...

### Education
Personalized learning and intelligent tutoring systems are reshaping education...

## Future Outlook
### Emerging Trends
- Autonomous AI agents
- Edge computing integration
- Quantum-AI hybrid systems

### Challenges and Opportunities
While AI presents immense opportunities, we must address challenges around ethics, safety, and regulation...

## Conclusion
The AI revolution is not just about technology—it's about reimagining what's possible...

GOAL_COMPLETED""",
            model="llama3.1"
        )
    
    async def _analyst_response(self, prompt: str):
        """Data analyst responses."""
        return OllamaResponse(
            content="""Data Analysis Report: AI Market Performance

**Key Metrics:**
- Market Size: $150.2B (2024)
- YoY Growth: +37.3%
- Investment Volume: $52.1B
- Active Companies: 15,000+

**Performance Indicators:**
📈 Revenue Growth: 35% average across top 100 AI companies
📊 Adoption Rate: 68% of enterprises using AI in some capacity
💰 ROI: Average 15-20% improvement in operational efficiency

**Segment Analysis:**
1. **NLP/LLMs**: 40% market share, highest growth
2. **Computer Vision**: 25% market share, stable growth
3. **Robotics**: 20% market share, emerging applications
4. **Predictive Analytics**: 15% market share, mature market

**Geographic Distribution:**
- North America: 45% of market value
- Asia-Pacific: 30% of market value
- Europe: 20% of market value
- Other regions: 5% of market value

**Risk Assessment:**
- Regulatory uncertainty: Medium risk
- Competition intensity: High risk
- Technology obsolescence: Low risk
- Market saturation: Low risk

**Recommendations:**
1. Focus on enterprise AI solutions
2. Invest in multimodal capabilities
3. Develop edge AI offerings
4. Strengthen data privacy measures

GOAL_COMPLETED""",
            model="llama3.1"
        )
    
    async def _manager_response(self, prompt: str):
        """Project manager responses."""
        return OllamaResponse(
            content="""Project Management Report: AI Market Analysis Initiative

**Project Status:** ✅ COMPLETED ON TIME

**Timeline Summary:**
- Project Duration: 5 days
- Tasks Completed: 12/12
- Milestones Achieved: 4/4
- Budget Utilization: 95%

**Team Performance:**
👥 **Research Team**: Excellent data gathering and analysis
📝 **Content Team**: High-quality deliverables, met all deadlines
📊 **Analytics Team**: Comprehensive data insights and visualizations
🔍 **QA Team**: Thorough review process, zero critical issues

**Deliverables Completed:**
1. ✅ Market research report (150 pages)
2. ✅ Executive summary (5 pages)
3. ✅ Data analysis dashboard
4. ✅ Presentation deck (25 slides)
5. ✅ Strategic recommendations

**Key Success Factors:**
- Clear communication channels
- Regular progress reviews
- Proactive risk management
- Strong team collaboration

**Lessons Learned:**
- Early stakeholder engagement crucial
- Data quality validation saves time
- Cross-functional collaboration enhances outcomes

**Next Steps:**
1. Present findings to executive team
2. Develop implementation roadmap
3. Allocate resources for priority initiatives
4. Schedule quarterly review meetings

**Overall Assessment:** 🌟 EXCEPTIONAL SUCCESS

GOAL_COMPLETED""",
            model="llama3.1"
        )
    
    async def _qa_response(self, prompt: str):
        """Quality assurance responses."""
        return OllamaResponse(
            content="""Quality Assurance Review Report

**Overall Quality Score: 94/100** ⭐⭐⭐⭐⭐

**Content Quality Assessment:**

📋 **Research Report**
- ✅ Accuracy: 98% (verified against 15 sources)
- ✅ Completeness: All required sections included
- ✅ Methodology: Sound research approach
- ⚠️ Minor: 2 formatting inconsistencies found and fixed

📊 **Data Analysis**
- ✅ Data integrity: All calculations verified
- ✅ Visualization quality: Clear and professional
- ✅ Statistical validity: Appropriate methods used
- ✅ Reproducibility: All steps documented

📝 **Written Content**
- ✅ Grammar and spelling: 99.8% accuracy
- ✅ Tone and style: Consistent throughout
- ✅ Readability: Appropriate for target audience
- ✅ Structure: Logical flow and organization

🎯 **Project Management**
- ✅ Timeline adherence: 100% on schedule
- ✅ Resource utilization: Within budget
- ✅ Communication: Clear and timely updates
- ✅ Risk management: Proactive approach

**Issues Identified and Resolved:**
1. 🔧 Fixed 2 minor formatting inconsistencies
2. 🔧 Standardized citation format across documents
3. 🔧 Updated 3 outdated statistics with latest data
4. 🔧 Enhanced visual consistency in charts

**Compliance Check:**
- ✅ Data privacy requirements met
- ✅ Industry standards followed
- ✅ Internal quality guidelines satisfied
- ✅ Stakeholder requirements fulfilled

**Recommendations for Future Projects:**
1. Implement automated formatting checks
2. Establish real-time data validation
3. Create standardized templates
4. Enhance cross-team review processes

**Final Approval:** ✅ APPROVED FOR DELIVERY

GOAL_COMPLETED""",
            model="llama3.1"
        )
    
    async def _general_response(self, prompt: str):
        """General responses."""
        return OllamaResponse(
            content="I understand the task and will work on it systematically.",
            model="llama3.1"
        )


class CustomAnalyticsTool(BaseTool):
    """Custom analytics tool for demonstration."""
    
    def __init__(self):
        super().__init__(
            name="analytics_dashboard",
            description="Generate analytics dashboard with charts and metrics",
            category="analytics"
        )
    
    async def execute(self, data_type: str, metrics: list = None) -> dict:
        """Generate mock analytics dashboard."""
        if metrics is None:
            metrics = ["growth", "performance", "trends"]
        
        # Mock dashboard data
        dashboard_data = {
            "data_type": data_type,
            "metrics": metrics,
            "charts": [
                {"type": "line", "title": f"{data_type} Growth Trend", "data_points": 12},
                {"type": "bar", "title": f"{data_type} Performance", "categories": 5},
                {"type": "pie", "title": f"{data_type} Distribution", "segments": 4}
            ],
            "kpis": {
                "total_value": "150.2B",
                "growth_rate": "37.3%",
                "market_share": "45%",
                "efficiency": "94%"
            },
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "message": f"Analytics dashboard for {data_type} generated successfully"
        }


async def print_section_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")


async def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")


async def demonstrate_basic_features(orchestrator: AgentOrchestrator):
    """Demonstrate basic framework features."""
    await print_section_header("BASIC FEATURES DEMONSTRATION")
    
    # Show available tools
    await print_subsection("Available Tools")
    tools = orchestrator.tool_registry.get_all_tools()
    for tool in tools:
        print(f"  🔧 {tool.name}: {tool.description}")
    
    # Show agent capabilities
    await print_subsection("Agent Capabilities")
    agents = orchestrator.get_all_agents()
    for agent in agents:
        print(f"  🤖 {agent.role} ({agent.agent_id})")
        for cap in agent.capabilities:
            print(f"    • {cap.name}: {cap.description}")


async def demonstrate_single_agent_tasks(orchestrator: AgentOrchestrator):
    """Demonstrate single agent task execution."""
    await print_section_header("SINGLE AGENT TASK EXECUTION")
    
    # Get research agent
    research_agent = None
    for agent in orchestrator.get_all_agents():
        if agent.role == "Research Specialist":
            research_agent = agent
            break
    
    if research_agent:
        await print_subsection("Research Task")
        
        task_id = await orchestrator.create_task(
            description="Conduct comprehensive market analysis of the AI industry",
            priority=8,
            context={"scope": "global", "timeframe": "2024", "focus": "trends and opportunities"}
        )
        
        await orchestrator.assign_task_to_agent(task_id, research_agent.agent_id)
        print(f"✅ Assigned research task to {research_agent.role}")
        
        # Wait for completion
        await asyncio.sleep(3)
        
        task = orchestrator.get_task(task_id)
        print(f"📊 Task status: {task.status.value}")


async def demonstrate_multi_agent_workflow(orchestrator: AgentOrchestrator):
    """Demonstrate multi-agent workflow execution."""
    await print_section_header("MULTI-AGENT WORKFLOW EXECUTION")
    
    # Create comprehensive workflow
    workflow = Workflow(
        name="AI Market Report Generation",
        description="Collaborative workflow to create a comprehensive AI market report",
        steps=[
            WorkflowStep(
                id="research_phase",
                description="Conduct market research and data collection",
                agent_role="Research Specialist",
                dependencies=[],
                context={"research_depth": "comprehensive", "sources": "multiple"}
            ),
            WorkflowStep(
                id="analysis_phase",
                description="Analyze collected data and generate insights",
                agent_role="Data Analyst",
                dependencies=["research_phase"],
                context={"analysis_type": "quantitative", "visualizations": True}
            ),
            WorkflowStep(
                id="writing_phase",
                description="Write comprehensive market report",
                agent_role="Content Writer",
                dependencies=["analysis_phase"],
                context={"format": "executive_report", "audience": "C-level"}
            ),
            WorkflowStep(
                id="management_phase",
                description="Coordinate project and ensure quality delivery",
                agent_role="Project Manager",
                dependencies=["writing_phase"],
                context={"deliverables": "report_package", "timeline": "immediate"}
            ),
            WorkflowStep(
                id="qa_phase",
                description="Quality assurance and final review",
                agent_role="Quality Assurance",
                dependencies=["management_phase"],
                context={"review_type": "comprehensive", "standards": "enterprise"}
            )
        ],
        context={"project_priority": "high", "deadline": "end_of_week"}
    )
    
    await print_subsection("Workflow Execution")
    print(f"📋 Workflow: {workflow.name}")
    print(f"📝 Description: {workflow.description}")
    print(f"🔄 Steps: {len(workflow.steps)}")
    
    # Execute workflow
    success = await orchestrator.execute_workflow(workflow)
    
    if success:
        print("✅ Workflow started successfully")
        
        # Monitor progress
        await print_subsection("Progress Monitoring")
        
        for i in range(10):  # Monitor for 20 seconds
            agent_statuses = {}
            for agent in orchestrator.get_all_agents():
                agent_statuses[agent.role] = agent.get_status().value
            
            print(f"⏱️  Step {i+1}: {agent_statuses}")
            await asyncio.sleep(2)
        
        print("🎉 Workflow execution completed!")
    else:
        print("❌ Failed to start workflow")


async def demonstrate_memory_and_learning(orchestrator: AgentOrchestrator):
    """Demonstrate memory management and learning capabilities."""
    await print_section_header("MEMORY AND LEARNING CAPABILITIES")
    
    await print_subsection("Memory Statistics")
    
    # Get memory statistics for each agent
    for agent in orchestrator.get_all_agents():
        stats = await orchestrator.memory_manager.get_memory_stats(agent.agent_id)
        print(f"🧠 {agent.role}:")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Memory types: {stats['memories_by_type']}")
        print(f"   Avg importance: {stats['average_importance']:.2f}")
    
    await print_subsection("Recent Memories")
    
    # Show recent memories from each agent
    for agent in orchestrator.get_all_agents():
        memories = await orchestrator.memory_manager.retrieve_memories(
            agent_id=agent.agent_id,
            limit=3
        )
        
        print(f"📝 {agent.role} recent memories:")
        for i, memory in enumerate(memories, 1):
            print(f"   {i}. {memory[:60]}...")


async def demonstrate_tool_usage(orchestrator: AgentOrchestrator):
    """Demonstrate tool usage and extensibility."""
    await print_section_header("TOOL USAGE AND EXTENSIBILITY")
    
    await print_subsection("Tool Categories")
    
    categories = orchestrator.tool_registry.get_categories()
    for category in categories:
        tools = orchestrator.tool_registry.get_tools_by_category(category)
        print(f"📂 {category.title()}: {len(tools)} tools")
        for tool in tools:
            print(f"   • {tool.name}")
    
    await print_subsection("Custom Tool Demonstration")
    
    # Execute custom analytics tool
    try:
        result = await orchestrator.tool_registry.execute_tool(
            "analytics_dashboard",
            {"data_type": "AI Market", "metrics": ["growth", "adoption", "investment"]}
        )
        
        if result["success"]:
            dashboard = result["dashboard"]
            print(f"✅ {result['message']}")
            print(f"📊 Generated {len(dashboard['charts'])} charts")
            print(f"📈 KPIs: {dashboard['kpis']}")
        else:
            print(f"❌ Tool execution failed")
    
    except Exception as e:
        print(f"❌ Error executing tool: {e}")


async def demonstrate_communication(orchestrator: AgentOrchestrator):
    """Demonstrate inter-agent communication."""
    await print_section_header("INTER-AGENT COMMUNICATION")
    
    await print_subsection("Message Exchange")
    
    agents = orchestrator.get_all_agents()
    if len(agents) >= 2:
        sender = agents[0]
        recipient = agents[1]
        
        # Send message
        await orchestrator.send_message(
            sender_id=sender.agent_id,
            recipient_id=recipient.agent_id,
            content="The market research data is ready for analysis. Please proceed with the quantitative analysis phase.",
            message_type="collaboration"
        )
        
        print(f"📤 {sender.role} → {recipient.role}: Message sent")
        
        # Send response
        await orchestrator.send_message(
            sender_id=recipient.agent_id,
            recipient_id=sender.agent_id,
            content="Thank you! I'll begin the analysis immediately and have results within the hour.",
            message_type="collaboration"
        )
        
        print(f"📥 {recipient.role} → {sender.role}: Response sent")
        
        await print_subsection("Broadcast Communication")
        
        # Broadcast message
        await orchestrator.broadcast_message(
            sender_id=sender.agent_id,
            content="Project milestone achieved: Market research phase completed successfully!",
            message_type="announcement"
        )
        
        print(f"📢 {sender.role} → All agents: Broadcast sent")


async def show_final_statistics(orchestrator: AgentOrchestrator):
    """Show final framework statistics."""
    await print_section_header("FINAL STATISTICS AND SUMMARY")
    
    await print_subsection("Framework Statistics")
    
    # Agent statistics
    agent_stats = orchestrator.get_agent_status_summary()
    print(f"🤖 Agent Status Summary: {agent_stats}")
    
    # Task statistics
    task_stats = orchestrator.get_task_status_summary()
    print(f"📋 Task Status Summary: {task_stats}")
    
    # Tool statistics
    tool_count = orchestrator.tool_registry.get_tool_count()
    print(f"🔧 Total Tools Available: {tool_count}")
    
    # Memory statistics
    total_memory_stats = await orchestrator.memory_manager.get_memory_stats()
    print(f"🧠 Total Memory Entries: {total_memory_stats['total_memories']}")
    
    await print_subsection("Performance Metrics")
    
    print(f"✅ Agents Created: {len(orchestrator.get_all_agents())}")
    print(f"✅ Tasks Executed: {len(orchestrator.get_all_tasks())}")
    print(f"✅ Workflows Completed: 1")
    print(f"✅ Messages Exchanged: Multiple")
    print(f"✅ Tools Utilized: {len(orchestrator.tool_registry.get_categories())} categories")


async def main():
    """Main comprehensive demonstration function."""
    print("🌟 OLLAMA AGENTIC FRAMEWORK")
    print("🌟 COMPREHENSIVE DEMONSTRATION")
    print("🌟 " + "="*50)
    
    # Initialize framework
    print("\n🔧 Initializing Framework Components...")
    
    ollama_integration = AdvancedMockOllamaIntegrationLayer()
    await ollama_integration.initialize()
    
    tool_registry = ToolRegistry()
    
    # Add custom analytics tool
    analytics_tool = CustomAnalyticsTool()
    tool_registry.register_tool(analytics_tool)
    
    memory_manager = MemoryManager(db_path=":memory:")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator(
        ollama_integration=ollama_integration,
        tool_registry=tool_registry,
        memory_manager=memory_manager
    )
    
    # Create diverse team of agents
    print("👥 Creating Agent Team...")
    
    # Research Specialist
    orchestrator.register_agent(
        agent_id="researcher_001",
        role="Research Specialist",
        description="Conducts comprehensive market research and data collection",
        capabilities=[
            AgentCapability(name="market_research", description="Analyze market trends and opportunities"),
            AgentCapability(name="data_collection", description="Gather data from multiple sources"),
            AgentCapability(name="competitive_analysis", description="Analyze competitive landscape")
        ]
    )
    
    # Data Analyst
    orchestrator.register_agent(
        agent_id="analyst_001",
        role="Data Analyst",
        description="Analyzes data and generates actionable insights",
        capabilities=[
            AgentCapability(name="statistical_analysis", description="Perform statistical analysis"),
            AgentCapability(name="data_visualization", description="Create charts and dashboards"),
            AgentCapability(name="predictive_modeling", description="Build predictive models")
        ]
    )
    
    # Content Writer
    orchestrator.register_agent(
        agent_id="writer_001",
        role="Content Writer",
        description="Creates engaging and informative content",
        capabilities=[
            AgentCapability(name="technical_writing", description="Write technical documentation"),
            AgentCapability(name="report_generation", description="Generate comprehensive reports"),
            AgentCapability(name="content_strategy", description="Develop content strategies")
        ]
    )
    
    # Project Manager
    orchestrator.register_agent(
        agent_id="manager_001",
        role="Project Manager",
        description="Coordinates projects and ensures successful delivery",
        capabilities=[
            AgentCapability(name="project_planning", description="Plan and organize projects"),
            AgentCapability(name="resource_management", description="Manage resources and timelines"),
            AgentCapability(name="stakeholder_communication", description="Communicate with stakeholders")
        ]
    )
    
    # Quality Assurance
    orchestrator.register_agent(
        agent_id="qa_001",
        role="Quality Assurance",
        description="Ensures quality and compliance of all deliverables",
        capabilities=[
            AgentCapability(name="quality_review", description="Review content for quality"),
            AgentCapability(name="compliance_check", description="Ensure compliance with standards"),
            AgentCapability(name="process_improvement", description="Improve processes and workflows")
        ]
    )
    
    print(f"✅ Created {len(orchestrator.get_all_agents())} specialized agents")
    
    # Start orchestrator
    await orchestrator.start()
    
    # Run demonstrations
    try:
        await demonstrate_basic_features(orchestrator)
        await demonstrate_single_agent_tasks(orchestrator)
        await demonstrate_multi_agent_workflow(orchestrator)
        await demonstrate_memory_and_learning(orchestrator)
        await demonstrate_tool_usage(orchestrator)
        await demonstrate_communication(orchestrator)
        await show_final_statistics(orchestrator)
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
    
    finally:
        # Stop orchestrator
        await orchestrator.stop()
    
    # Final message
    await print_section_header("DEMONSTRATION COMPLETED")
    print("🎉 The Ollama Agentic Framework demonstration has completed successfully!")
    print("🚀 The framework is ready for production use with real Ollama models.")
    print("📚 Check the documentation for detailed usage instructions.")
    print("🔧 Customize agents, tools, and workflows for your specific needs.")
    print("\n✨ Thank you for exploring the Ollama Agentic Framework! ✨")


if __name__ == "__main__":
    asyncio.run(main())

