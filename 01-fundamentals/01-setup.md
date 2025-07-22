# 1. Environment Setup

This guide will walk you through setting up your development environment for Azure AI Foundry agents development.

## 🎯 Objectives

- Create an Azure AI Foundry project
- Set up Python development environment
- Configure authentication and environment variables
- Validate your setup with a test connection

## ⏱️ Estimated Time: 30 minutes

## 📋 Prerequisites

- Azure subscription with Owner or Contributor permissions
- Python 3.9+ installed
- Git installed
- Code editor (VS Code recommended)

## 🚀 Step-by-Step Setup

### Step 1: Create Azure AI Foundry Project (10 minutes)

1. **Navigate to Azure AI Foundry portal:**
   - Go to [https://ai.azure.com](https://ai.azure.com)
   - Sign in with your Azure credentials

2. **Create a new project:**
   - Click "Create new project"
   - Choose "Foundry project" (not hub-based)
   - Select your subscription and resource group
   - Choose a unique project name (e.g., "ai-agents-learning")
   - Select a region (recommend: East US 2, West US 2, or West Europe)
   - Click "Create"

3. **Deploy a model:**
   - In your project, go to "Models + endpoints"
   - Click "Deploy model" → "Real-time endpoint"
   - Select "gpt-4o-mini" model
   - Use default deployment settings
   - Name your deployment "gpt-4o-mini"
   - Click "Deploy"

4. **Note your project details:**
   - Project endpoint (found in Overview page)
   - Subscription ID
   - Resource group name
   - Project name

### Step 2: Python Environment Setup (10 minutes)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ai-agents-system
   ```

2. **Create and activate virtual environment:**
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

### Step 3: Authentication Setup (5 minutes)

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

4. **Verify authentication:**
   ```bash
   az account show
   ```

### Step 4: Environment Variables Configuration (5 minutes)

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

3. **Secure your .env file:**
   ```bash
   # Add .env to .gitignore if not already there
   echo ".env" >> .gitignore
   ```

## ✅ Validation

Run the following validation script to ensure everything is set up correctly:

```python
# exercises/exercise_1_setup.py
import os
import asyncio
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

async def validate_setup():
    """Validate Azure AI Foundry setup"""
    load_dotenv()
    
    # Check environment variables
    required_vars = [
        'PROJECT_ENDPOINT',
        'MODEL_DEPLOYMENT_NAME',
        'AZURE_SUBSCRIPTION_ID',
        'PROJECT_NAME'
    ]
    
    print("🔍 Checking environment variables...")
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Missing required environment variable: {var}")
            return False
        else:
            print(f"✅ {var}: Set")
    
    # Test Azure authentication
    print("\n🔐 Testing Azure authentication...")
    try:
        credential = DefaultAzureCredential()
        # Get a token to verify authentication works
        token = credential.get_token("https://management.azure.com/.default")
        print("✅ Azure authentication successful")
    except Exception as e:
        print(f"❌ Azure authentication failed: {e}")
        return False
    
    # Test Azure AI Project connection
    print("\n🤖 Testing Azure AI Project connection...")
    try:
        client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential()
        )
        
        # List deployments to verify connection
        deployments = list(client.deployments.list())
        print(f"✅ Connected to Azure AI Project successfully")
        print(f"✅ Found {len(deployments)} model deployments")
        
        # Check if our target model is deployed
        target_model = os.getenv('MODEL_DEPLOYMENT_NAME')
        model_found = any(d.name == target_model for d in deployments)
        if model_found:
            print(f"✅ Target model '{target_model}' found and accessible")
        else:
            print(f"⚠️  Target model '{target_model}' not found. Available models:")
            for d in deployments:
                print(f"   - {d.name}")
    
    except Exception as e:
        print(f"❌ Azure AI Project connection failed: {e}")
        return False
    
    print("\n🎉 Setup validation completed successfully!")
    print("You're ready to create your first agent!")
    return True

if __name__ == "__main__":
    asyncio.run(validate_setup())
```

Run the validation:
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

---

**Need help?** Check the [troubleshooting section](#-troubleshooting) above or review the [FAQ](../docs/FAQ.md).
