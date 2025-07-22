# DevContainer for Azure AI Foundry Agents

Simple devcontainer setup for Azure AI Foundry Agents development.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Quick Start

1. Open project in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select "Dev Containers: Reopen in Container"
4. Wait for setup to complete
5. Configure your `.env` file with Azure settings
6. Run `python setup_system.py` to validate setup

## What's Included

- Python 3.11
- Azure CLI
- Required Python packages (automatically installed from requirements.txt)
- Essential VS Code extensions for Python and Azure development

## Environment Setup

Create a `.env` file with your Azure AI Foundry configuration:

```
PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
MODEL_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP_NAME=your-resource-group
AZURE_AI_PROJECT_NAME=your-project-name
```

## Running the Code

```bash
# Setup and validate environment
python setup_system.py

# Run main application
python main_application.py

# Run tests
python run_comprehensive_tests.py
```

That's it! Simple and straightforward.
