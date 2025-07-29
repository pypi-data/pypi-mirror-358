# Installation and Setup Guide

This comprehensive guide will walk you through the installation and setup process for the Ollama Agentic Framework, ensuring you have everything configured correctly for optimal performance.

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11
- **Python**: Version 3.11 or higher
- **Memory**: 8GB RAM minimum (16GB recommended for complex workflows)
- **Storage**: 2GB free space for the framework and dependencies
- **Network**: Internet connection for downloading models and dependencies

### Recommended Requirements
- **Operating System**: Linux (Ubuntu 22.04+) or macOS (12.0+)
- **Python**: Version 3.11 or 3.12
- **Memory**: 16GB RAM or higher
- **Storage**: 10GB+ free space for models and data
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster model inference)

## Prerequisites

### 1. Python Installation

Ensure you have Python 3.11 or higher installed on your system.

**Check your Python version:**
```bash
python3 --version
```

**Install Python 3.11+ if needed:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

**macOS (using Homebrew):**
```bash
brew install python@3.11
```

**Windows:**
Download and install from [python.org](https://www.python.org/downloads/)

### 2. Ollama Installation

The framework requires Ollama to be installed and running on your system.

**Install Ollama:**

**Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download the installer from [ollama.ai](https://ollama.ai/download)

**Verify Ollama installation:**
```bash
ollama --version
```

**Start Ollama service:**
```bash
ollama serve
```

The Ollama service should now be running on `http://localhost:11434`

### 3. Git Installation

Git is required for cloning the repository and version control.

**Install Git:**

**Ubuntu/Debian:**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

**Windows:**
Download from [git-scm.com](https://git-scm.com/download/win)

## Framework Installation

### Method 1: Installation from Source (Recommended)

This method gives you access to the latest features and allows for easy customization.

**1. Clone the repository:**
```bash
git clone https://github.com/madnansultandotme/ollama-agentic-framework.git
cd ollama-agentic-framework
```

**2. Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Upgrade pip:**
```bash
pip install --upgrade pip
```

**4. Install dependencies:**
```bash
pip install -r requirements.txt
```

**5. Install the framework in development mode:**
```bash
pip install -e .
```

### Method 2: Installation from PyPI (Future)

Once published to PyPI, you can install directly:

```bash
pip install edgebrain
```

## Initial Configuration

### 1. Download Ollama Models

The framework works with various Ollama models. Download the models you plan to use:

**Recommended models:**
```bash
# General purpose model (recommended for most use cases)
ollama pull llama3.1

# Code generation model
ollama pull codellama

# Lightweight model for testing
ollama pull phi3

# Advanced reasoning model
ollama pull mistral
```

**Verify models are available:**
```bash
ollama list
```

### 2. Environment Configuration

Create a `.env` file in the project root to configure environment variables:

```bash
# .env file
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.1
MEMORY_DB_PATH=agent_memory.db
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=5
TOOL_TIMEOUT=30
```

### 3. Database Setup

The framework uses SQLite for memory storage. The database will be created automatically on first run, but you can initialize it manually:

```python
from src.memory.memory_manager import MemoryManager

# Initialize memory manager (creates database if it doesn't exist)
memory_manager = MemoryManager(db_path="agent_memory.db")
```

## Verification

### 1. Run Basic Tests

Verify your installation by running the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test
python -m pytest tests/test_ollama_integration.py -v
```

### 2. Run Example Scripts

Test the framework with the provided examples:

```bash
# Simple research agent example
python examples/simple_research_agent.py

# Comprehensive demo (requires all components)
python examples/comprehensive_demo.py
```

### 3. Check Component Status

Verify all components are working correctly:

```python
import asyncio
from src.integration.ollama_client import OllamaIntegrationLayer
from src.tools.tool_registry import ToolRegistry
from src.memory.memory_manager import MemoryManager

async def check_components():
    # Test Ollama connection
    ollama = OllamaIntegrationLayer()
    if await ollama.initialize():
        print("✅ Ollama integration working")
        models = ollama.get_available_models()
        print(f"📦 Available models: {models}")
    else:
        print("❌ Ollama integration failed")
    
    # Test tool registry
    tools = ToolRegistry()
    print(f"🔧 Available tools: {tools.get_tool_count()}")
    
    # Test memory manager
    memory = MemoryManager()
    print("🧠 Memory manager initialized")

# Run the check
asyncio.run(check_components())
```

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

**Problem**: Cannot connect to Ollama service
**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Check firewall settings
sudo ufw allow 11434
```

#### 2. Python Version Issues

**Problem**: Framework requires Python 3.11+
**Solution**:
```bash
# Install Python 3.11 using pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 3. Memory/Performance Issues

**Problem**: High memory usage or slow performance
**Solution**:
- Use smaller models (phi3 instead of llama3.1)
- Reduce max_concurrent_agents in configuration
- Increase system RAM or use swap space
- Enable GPU acceleration if available

#### 4. Import Errors

**Problem**: Module import errors
**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 5. Database Permissions

**Problem**: SQLite database permission errors
**Solution**:
```bash
# Check file permissions
ls -la agent_memory.db

# Fix permissions
chmod 664 agent_memory.db

# Or use in-memory database for testing
export MEMORY_DB_PATH=":memory:"
```

### Performance Optimization

#### 1. Model Selection

Choose appropriate models based on your use case:

- **Development/Testing**: `phi3` (lightweight, fast)
- **General Purpose**: `llama3.1` (balanced performance)
- **Code Generation**: `codellama` (specialized for coding)
- **Advanced Reasoning**: `mistral` (high quality, slower)

#### 2. Memory Configuration

Optimize memory usage:

```python
# Use in-memory database for temporary workloads
memory_manager = MemoryManager(db_path=":memory:")

# Limit memory retention
memory_manager.set_retention_policy(max_memories=1000, max_age_days=30)
```

#### 3. Concurrent Processing

Configure concurrency based on your system:

```python
# Limit concurrent agents based on available resources
orchestrator = AgentOrchestrator(
    max_concurrent_agents=3,  # Adjust based on RAM
    task_timeout=60           # Prevent hanging tasks
)
```

## Advanced Configuration

### 1. Custom Model Configuration

Configure specific models for different agent types:

```python
# Agent-specific model configuration
research_agent = orchestrator.register_agent(
    agent_id="researcher_001",
    role="Research Specialist",
    model="llama3.1",  # Use specific model
    model_params={
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2048
    }
)
```

### 2. Tool Configuration

Configure custom tools and tool categories:

```python
from src.tools.tool_registry import BaseTool

class DatabaseTool(BaseTool):
    def __init__(self, connection_string):
        super().__init__(
            name="database_query",
            description="Execute database queries",
            category="data"
        )
        self.connection_string = connection_string
    
    async def execute(self, query: str) -> dict:
        # Database query implementation
        pass

# Register custom tool
tool_registry.register_tool(DatabaseTool("sqlite:///data.db"))
```

### 3. Logging Configuration

Set up comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_framework.log'),
        logging.StreamHandler()
    ]
)

# Set specific log levels
logging.getLogger('src.core.agent').setLevel(logging.DEBUG)
logging.getLogger('src.integration.ollama_client').setLevel(logging.INFO)
```

### 4. Security Configuration

Implement security best practices:

```python
# Secure tool execution
tool_registry.set_security_policy({
    "allow_file_operations": False,
    "allow_network_access": True,
    "sandbox_mode": True,
    "max_execution_time": 30
})

# Memory encryption (for sensitive data)
memory_manager = MemoryManager(
    db_path="encrypted_memory.db",
    encryption_key="your-encryption-key"
)
```

## Next Steps

After successful installation and configuration:

1. **Read the API Documentation**: Familiarize yourself with the framework's API
2. **Explore Examples**: Run and modify the provided examples
3. **Create Your First Agent**: Build a simple agent for your specific use case
4. **Join the Community**: Participate in discussions and contribute to the project

## Getting Help

If you encounter issues during installation:

1. **Check the FAQ**: Common issues and solutions
2. **Search Issues**: Look for similar problems on GitHub
3. **Create an Issue**: Report new bugs or request help
4. **Join Discussions**: Ask questions in the community forum

---

**Installation complete! You're ready to start building with the Ollama Agentic Framework.**

