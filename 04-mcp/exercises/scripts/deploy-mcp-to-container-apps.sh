#!/bin/bash

# Configuration
RESOURCE_GROUP="rg-multi-agents"
LOCATION="westus2"  # Choose a location that supports Container Apps
CONTAINER_APP_ENV="mcp-server-env"
CONTAINER_APP_NAME="mcp-sqlite-server"
REGISTRY_NAME="mcpsqliteregistry"
IMAGE_NAME="mcp-sqlite-server"

echo "🚀 Deploying MCP SQLite Server to Azure Container Apps"
echo "====================================================="

# Check if logged in to Azure
echo "📝 Checking Azure login..."
if ! az account show > /dev/null 2>&1; then
    echo "❌ Not logged in to Azure. Running 'az login'..."
    az login
fi

# Use existing resource group from .env
echo "📦 Using resource group: $RESOURCE_GROUP"

# Create Container Registry (if not exists)
echo "🏗️  Creating Container Registry..."
if ! az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $REGISTRY_NAME \
        --sku Basic \
        --admin-enabled true
fi

# Get registry credentials
REGISTRY_SERVER=$(az acr show --name $REGISTRY_NAME --query loginServer -o tsv)
REGISTRY_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Show what's changed
echo "📝 Files being deployed:"
echo "========================"
ls -la *.py
echo ""
echo "📄 setup_sqlite_mcp_server.py last modified: $(stat -c %y setup_sqlite_mcp_server.py 2>/dev/null || stat -f %Sm setup_sqlite_mcp_server.py)"
echo ""

# Build and push Docker image
echo "🐳 Building Docker image..."
BUILD_TIMESTAMP=$(date +%s)

# Create a unique tag to force fresh build
IMAGE_TAG="latest-$BUILD_TIMESTAMP"

az acr build \
    --registry $REGISTRY_NAME \
    --image $IMAGE_NAME:$IMAGE_TAG \
    --image $IMAGE_NAME:latest \
    --file Dockerfile \
    .

# Create Container Apps Environment (if not exists)
echo "🌍 Creating Container Apps Environment..."
if ! az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
fi

# Deploy Container App
echo "🚀 Deploying Container App..."
REVISION_SUFFIX="rev-$(date +%s)"

# Check if container app exists
if az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1; then
    echo "📦 Updating existing container app..."
    # Update with new image - this forces a new revision
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image $REGISTRY_SERVER/$IMAGE_NAME:latest \
        --revision-suffix $REVISION_SUFFIX \
        --set-env-vars "PROTOCOL_VERSION=2025-03-26"
else
    echo "📦 Creating new container app..."
    # Create new container app
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINER_APP_ENV \
        --image $REGISTRY_SERVER/$IMAGE_NAME:latest \
        --target-port 3000 \
        --ingress 'external' \
        --registry-server $REGISTRY_SERVER \
        --registry-username $REGISTRY_USERNAME \
        --registry-password $REGISTRY_PASSWORD \
        --cpu 0.5 \
        --memory 1.0 \
        --min-replicas 1 \
        --max-replicas 3
fi

# Get the public URL
PUBLIC_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "✅ Deployment Complete!"
echo "====================================================="
echo "🌐 MCP Server URL: https://$PUBLIC_URL"
echo "📅 Deployed at: $(date)"
echo "🏷️  Revision: $REVISION_SUFFIX"
echo ""
echo "📝 Update your .env file:"
echo "MCP_SERVER_URL=https://$PUBLIC_URL"
echo ""
echo "🧪 Test the deployment:"
echo "curl https://$PUBLIC_URL/health"

# Optional: Test the deployment
echo ""
echo "🧪 Testing deployment..."
sleep 10  # Give the container time to start
if curl -s -f https://$PUBLIC_URL/health > /dev/null; then
    echo "✅ Health check passed!"
    echo "Response: $(curl -s https://$PUBLIC_URL/health)"
    
    # Test capabilities endpoint
    echo ""
    echo "📋 Testing capabilities endpoint..."
    curl -s https://$PUBLIC_URL/capabilities | jq .
else
    echo "⚠️  Health check failed. Container might still be starting..."
    echo "Check logs with: az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP"
fi

# Show how to monitor the container
echo ""
echo "📊 Monitor your container:"
echo "az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --follow"
