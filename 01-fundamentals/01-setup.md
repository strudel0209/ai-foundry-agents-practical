# 1. Environment Setup

This guide will walk you through setting up your development environment for Azure AI Foundry agents development.

## 🎯 Objectives

- Create an Azure AI Foundry project
- Set up Python development environment
- Configure authentication and environment variables
- Validate your setup with a test connection

## 📋 Prerequisites

- Azure subscription with Owner or Contributor permissions
- Python 3.9+ installed
- Git installed

## 🚀 Step-by-Step Setup

### Step 1: Create Azure AI Foundry Project

1. **Navigate to Azure AI Foundry portal:**
   - Go to [https://ai.azure.com](https://ai.azure.com)
   - Sign in with your Azure credentials

2. **Create a new project:**
   - Click "Create new project"
   - Choose "Foundry project" (not hub-based)
   - Select your subscription and resource group
   - Choose a unique project name (e.g., "ai-agents-learning")
   - Select a region (recommend: East US 2, West US 2, or West Europe)

3. **Deploy a model:**
   - In your project, go to "Models + endpoints"
   - Click "Deploy model" → "Real-time endpoint"
   - Select "gpt-4o-mini" model
   - Use default deployment settings
   - Name your deployment "gpt-4o-mini"

4. **Note your project details:**
   - Project endpoint (found in Overview page)
   - Subscription ID
   - Resource group name
   - Project name

### Step 2: Python Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ai-agents-system
   ```

2. **Create and activate virtual environment (if not using DevContainers):**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python -c "import azure.ai.projects; print('Azure AI Projects SDK installed successfully')"
   python -c "import azure.identity; print('Azure Identity SDK installed successfully')"
   ```

### Step 3: Authentication Setup

1. **Install Azure CLI (if not already installed):**
   - Download from [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

2. **Login to Azure:**
   ```bash
   az login
   ```

3. **Set default subscription:**
   ```bash
   az account set --subscription "your-subscription-id"
   ```

### Step 4: Environment Variables Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Edit the .env file with your values:**
   ```env
   # Required values
   PROJECT_ENDPOINT=https://your-resource-name.services.ai.azure.com/api/projects/your-project-name
   MODEL_DEPLOYMENT_NAME=gpt-4o-mini
   AZURE_SUBSCRIPTION_ID=your-subscription-id
   AZURE_RESOURCE_GROUP=your-resource-group-name
   PROJECT_NAME=your-project-name
   
   # Optional for advanced features
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   ```
## ✅ Validation

Run the following validation script to ensure everything is set up correctly:
```bash
cd 01-fundamentals
python exercises/exercise_1_setup.py
```

## 🔧 Troubleshooting

### Common Issues and Solutions

**Issue: "DefaultAzureCredential failed to retrieve a token"**
- Solution: Run `az login` and ensure you're authenticated
- Alternative: Check if you have the correct permissions

**Issue: "Project endpoint not found"**
- Solution: Verify your project endpoint format in Azure AI Foundry portal
- Format should be: `https://your-resource-name.services.ai.azure.com/api/projects/your-project-name`

**Issue: "Model deployment not found"**
- Solution: Ensure you've deployed the gpt-4o-mini model in your Azure AI Foundry project
- Check the deployment name matches your environment variable

**Issue: "Permission denied"**
- Solution: Ensure your account has "Azure AI User" role on the project scope
- Contact your Azure administrator if needed

### Verification Checklist

Before proceeding to the next lesson, ensure:

- ✅ Azure AI Foundry project created successfully
- ✅ Python virtual environment activated
- ✅ All required packages installed
- ✅ Azure CLI authentication working
- ✅ Environment variables configured
- ✅ Validation script runs without errors
- ✅ Can connect to Azure AI Project
- ✅ Target model deployment accessible

## 📖 Additional Resources

- [Azure AI Foundry Project Setup Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code)
- [Azure CLI Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [DefaultAzureCredential Documentation](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)

## ➡️ Next Step

Once your setup validation passes, proceed to [Creating Your First Agent](./02-basic-agent.md).

