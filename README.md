# Azure AI Foundry Agents Learning System

A comprehensive, hands-on learning system for building production-ready AI agents with Azure AI Foundry, including native Model Context Protocol (MCP) support, multi-agent orchestration, and enterprise deployment patterns.

## 🎯 What You'll Build

- **Intelligent AI Agents** with Azure AI Foundry's native capabilities
- **Multi-Agent Systems** using Semantic Kernel orchestration
- **MCP Servers** for extending agents with external tools and databases
- **Production-Ready Solutions** with monitoring, scaling, and security

## 📋 Prerequisites

- **Azure Subscription** with Contributor access
- **Python 3.11+** (Python 3.12+ recommended for MCP features)
- **Azure AI Foundry Project** with deployed models (e.g., gpt-4o-mini)
- **Azure CLI** authenticated (`az login`)
- **Docker Desktop** (for containerized deployments)

## 🚀 Quick Start

### Option 1: Using Dev Container (Recommended)

The easiest way to get started is using the pre-configured dev container in VS Code:

```bash
# Clone the repository
git clone <repository-url>
cd ai-agents-system

# Open in VS Code
code .
```

1. **Install Dev Containers extension**: 
   - In VS Code, install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   
2. **Reopen in Container**:
   - Press `F1` or `Ctrl+Shift+P` to open command palette
   - Select **"Dev Containers: Reopen in Container"**
   - VS Code will build and start the container automatically

### Option 2: Local Python Environment

If you prefer to work locally without containers:

```bash
# Clone the repository
git clone <repository-url>
cd ai-agents-system

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment (Both Options)

```bash
# Configure environment
cp .env.template .env
# Edit .env with your Azure credentials

# Validate setup
python setup_system.py
```

> **💡 Pro Tip**: The dev container includes all necessary tools pre-configured, including Python 3.12+, Azure CLI, Node.js (for MCP servers), and development extensions. It's the fastest way to get started!

## 📚 Learning Modules

### [Module 1: Fundamentals](01-fundamentals/README.md) 
Master the basics of Azure AI Foundry agents.

**What you'll learn:**
- Azure AI Foundry project setup and authentication
- Agent creation with the latest SDK patterns
- Thread and run management for conversations
- Agent lifecycle and resource management

**Key exercises:**
- `exercise_1_setup.py` - Environment validation
- `exercise_2_basic_agent.py` - First agent creation
- `exercise_3_conversation.py` - Multi-turn conversations

### [Module 2: Tools Mastery](02-tools/README.md)
Unlock the full potential of agent tools.

**What you'll learn:**
- **File Search** - RAG with vector stores for document intelligence
- **Code Interpreter** - Dynamic Python execution and data analysis
- **Function Calling** - Custom business logic integration

**Key exercises:**
- `exercise_1_file_search.py` - Document search and retrieval
- `exercise_2_code_interpreter.py` - Data visualization and analysis
- `exercise_3_function_calling.py` - Business logic integration

### [Module 3: Advanced Orchestration](03-orchestration/README.md)
Build sophisticated multi-agent systems.

**What you'll learn:**
- Semantic Kernel integration for agent coordination
- Memory management with vector stores
- Intelligent routing and workflow automation
- Enterprise orchestration patterns

**Key exercises:**
- `exercise_2_semantic_kernel.py` - SK integration basics
- `exercise_3_advanced_orchestration.py` - Multi-agent workflows with memory

### [Module 4: MCP Integration](04-mcp/README.md)
Connect agents to external systems using Model Context Protocol.

**What you'll learn:**
- MCP protocol fundamentals and architecture
- Building MCP servers for tool exposure
- Native Azure AI Foundry MCP integration (July 2025 feature)
- Deploying MCP servers to Azure Container Apps

**Key components:**
- `exercise_1_mocking_mcp_server.py` - Basic MCP server implementation
- `exercise_2_mcp_agents.py` - Agent-MCP integration
- `setup_sqlite_mcp_server.py` - Production-ready MCP server
- `deploy-mcp-to-container-apps.sh` - Azure deployment automation

## 🏗️ Repository Structure

```
ai-agents-system/
├── 01-fundamentals/          # Agent basics and setup
├── 02-tools/                 # File search, code interpreter, functions
├── 03-orchestration/         # Multi-agent systems with SK
├── 04-mcp/                   # Model Context Protocol integration
│   ├── exercises/            # Hands-on MCP exercises
│   └── scripts/              # MCP server implementation & deployment
├── core/                     # Shared utilities and configuration
├── examples/                 # Complete working examples
├── tests/                    # Comprehensive test suite
└── .devcontainer/           # VS Code dev container setup
```

## 🔥 Key Features (July 2025)

### Native MCP Support in Azure AI Foundry
As of July 2025, Azure AI Foundry Agent Service includes native MCP support:

```python
# Direct MCP tool configuration
tools=[
    {
        "type": "mcp",
        "server_label": "sqlite_business",
        "server_url": "https://your-mcp-server.azurecontainerapps.io",
        "allowed_tools": ["sql_query", "list_tables"]
    }
]

# Runtime configuration with approval control
tool_resources={
    "mcp": [{
        "server_label": "sqlite_business",
        "require_approval": "never"
    }]
}
```

### Multi-Agent Orchestration with Semantic Kernel
Advanced coordination patterns with memory management:

```python
# Intelligent routing with memory-aware context
orchestrator = MultiAgentOrchestrator(
    vector_store_type="azure_ai_search",
    embedding_deployment=EMBEDDING_MODEL
)

# Collaborative workflows
result = await orchestrator.process_request(
    "Analyze Q3 financial performance and compliance"
)
```

### Production-Ready MCP Deployment
Automated deployment to Azure Container Apps:

```bash
# Deploy MCP server with one command
./deploy-mcp-to-container-apps.sh

# Automatic HTTPS endpoint provisioning
# Built-in health checks and monitoring
# Auto-scaling capabilities
```

## 💡 Best Practices

### Development Workflow
1. Start with local development using the devcontainer
2. Test MCP servers locally before cloud deployment
3. Use in-memory vector stores for development, Azure AI Search for production
4. Implement comprehensive error handling and logging

### Security Considerations
- Use Azure Managed Identity for authentication
- Implement proper CORS headers for MCP servers
- Validate all tool inputs and sanitize SQL queries
- Use approval workflows for sensitive operations

### Performance Optimization
- Cache frequently accessed data in vector stores
- Use async patterns for parallel agent execution
- Implement connection pooling for database access
- Monitor token usage and optimize prompts

## 🧪 Testing & Validation

```bash
# Run module-specific tests
python 01-fundamentals/exercises/exercise_1_setup.py

# Run comprehensive system tests
python tests/run_comprehensive_tests.py

# Test MCP server locally
python 04-mcp/exercises/scripts/setup_sqlite_mcp_server.py

# Validate Azure deployment
curl https://your-mcp-server.azurecontainerapps.io/health
```

## 📖 Additional Resources

### Official Documentation
- [Azure AI Foundry Agents](https://learn.microsoft.com/azure/ai-foundry/agents/)
- [Model Context Protocol Tool](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)
- [MCP Specification](https://modelcontextprotocol.io/)

### Reference Implementations
- [azure-ai-foundry/mcp-foundry](https://github.com/azure-ai-foundry/mcp-foundry)
- [AI-Gateway Sample](https://github.com/Azure-Samples/AI-Gateway)
- [Azure MCP Functions](https://github.com/Azure-Samples/remote-mcp-functions-dotnet)

### Community Resources
- [Azure AI Community](https://techcommunity.microsoft.com/t5/azure-ai/ct-p/AzureAI)
- [MCP Discord](https://discord.gg/mcp)
- [Stack Overflow - Azure AI Foundry](https://stackoverflow.com/questions/tagged/azure-ai-foundry)
