# Module 1: Azure AI Foundry Agent Fundamentals

Welcome to the foundational module of your Azure AI Foundry agents learning journey! This module will establish the core concepts and practical skills needed to work with Azure AI Foundry agents.

## 🎯 Module Objectives

By the end of this module, you will:

- Set up your Azure AI Foundry development environment
- Create your first Azure AI agent
- Understand the agent execution model (threads, runs, messages)
- Master basic agent lifecycle management
- Implement proper error handling and authentication

## 📋 Prerequisites

- Azure subscription with appropriate permissions
- Python 3.9+ installed
- Basic understanding of Python and REST APIs
- Git for version control

## 🕒 Estimated Time: 2-3 hours

## 📚 Learning Path

### 1. [Environment Setup](./01-setup.md) - 30 minutes
Learn how to:
- Configure Azure AI Foundry project
- Set up Python development environment
- Configure authentication and environment variables
- Validate your setup

### 2. [Creating Your First Agent](./02-basic-agent.md) - 45 minutes
Learn how to:
- Initialize the Azure AI Project client
- Create a basic agent with instructions
- Understand agent configuration options
- Test your agent

### 3. [Understanding Threads and Runs](./03-threads-runs.md) - 45 minutes
Learn how to:
- Create conversation threads
- Start and monitor agent runs
- Handle run states and polling
- Retrieve and display messages

### 4. [Agent Lifecycle Management](./04-lifecycle.md) - 30 minutes
Learn how to:
- List and retrieve agents
- Update agent configurations
- Delete agents and cleanup resources
- Best practices for agent management

## 🏗️ Project Structure

```
01-fundamentals/
├── README.md                 # This file
├── 01-setup.md              # Environment setup guide
├── 02-basic-agent.md         # First agent creation
├── 03-threads-runs.md        # Threads and runs deep dive
├── 04-lifecycle.md           # Agent lifecycle management
├── exercises/                # Hands-on exercises
│   ├── exercise_1_setup.py
│   ├── exercise_2_basic_agent.py
│   ├── exercise_3_conversation.py
│   └── exercise_4_management.py
├── solutions/                # Exercise solutions
│   ├── solution_1_setup.py
│   ├── solution_2_basic_agent.py
│   ├── solution_3_conversation.py
│   └── solution_4_management.py
└── assets/                   # Sample files and data
    ├── sample_instructions.txt
    └── test_conversation.json
```

## 🎯 Key Concepts Covered

### Agent Fundamentals
- **Agent**: Custom AI that uses AI models with tools and instructions
- **Instructions**: System prompts that define agent behavior
- **Model**: The underlying LLM (e.g., gpt-4o-mini) used by the agent

### Execution Model
- **Thread**: A conversation session between agent and user
- **Message**: Individual communications within a thread
- **Run**: Activation of an agent to process thread messages
- **Run Step**: Detailed execution steps during a run

### Client Architecture
- **AIProjectClient**: Main client for Azure AI Foundry operations
- **AgentsClient**: Specialized client for agent operations (accessed via `project_client.agents`)
- **Authentication**: Using DefaultAzureCredential for secure access

### Best Practices
- **Agent Reuse**: Always check for existing agents before creating new ones
- **Resource Management**: Clean up test agents to avoid accumulation
- **Error Handling**: Implement proper exception handling for all operations
- **SDK Method Usage**: Use correct method names (e.g., `create()` not `create_agent()`)

## 🚀 Quick Start

1. **Clone and navigate to this module:**
   ```bash
   cd 01-fundamentals
   ```

2. **Set up your environment:**
   ```bash
   # Copy the template and configure your variables
   cp ../.env.template .env
   # Edit .env with your Azure credentials
   ```

3. **Start with the setup guide:**
   - Open [01-setup.md](./01-setup.md)
   - Follow the step-by-step instructions
   - Complete the setup validation

4. **Progress through each lesson:**
   - Read the concepts
   - Run the code examples
   - Complete the exercises
   - Check your solutions

## 📊 Success Criteria

By the end of this module, you should be able to:

✅ Create an Azure AI Foundry project and configure authentication  
✅ Initialize an AIProjectClient and create agents programmatically  
✅ Implement agent reuse patterns to prevent duplicate agents  
✅ Start conversations using threads and process them with runs  
✅ Handle different run states and retrieve conversation history  
✅ Manage agent lifecycle including creation, updates, and deletion  
✅ Implement basic error handling and logging using correct SDK methods  

## 🔍 Common Issues and Troubleshooting

### Authentication Issues
- Ensure you're logged in with `az login`
- Verify your Azure subscription and resource group access
- Check that your service principal has the correct permissions

### Environment Setup Issues
- Validate Python version with `python --version`
- Ensure virtual environment is activated
- Check that all required packages are installed

### Agent Creation Issues
- Verify your project endpoint format
- Ensure your model deployment exists and is accessible
- Check resource quotas and availability

## 📖 Additional Resources

### Official Documentation
- [Azure AI Foundry Agents Overview](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview)
- [Azure AI Foundry SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Authentication Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-azure-ai-foundry)

### Code Examples
- [Azure SDK Python Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples)
- [Agent Examples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples)

## ➡️ Next Steps

Once you complete this module:

1. **Review your learning** by going through the exercises again
2. **Experiment** with different agent instructions and configurations
3. **Move to Module 2** - [Tools Exploration](../02-tools-exploration/README.md)

## 🤝 Support

If you encounter issues:
- Review the troubleshooting section above
- Check the [FAQ](../docs/FAQ.md)
- Open an issue in the repository

---

**Ready to begin?** Start with [Environment Setup](./01-setup.md) 🚀
