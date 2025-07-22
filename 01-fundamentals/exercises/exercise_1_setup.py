"""
Exercise 1: Environment Setup Validation

This script validates that your Azure AI Foundry development environment
is properly configured and ready for agent development.

Run this script after completing the setup guide to ensure everything works.
"""

import os
import asyncio
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

async def validate_setup():
    """Validate Azure AI Foundry setup"""
    
    # Load environment variables
    load_dotenv()
    
    success = True
    
    # Header
    console.print(Panel.fit(
        "🚀 Azure AI Foundry Agent Setup Validation",
        style="bold blue"
    ))
    
    # Check environment variables
    console.print("\n🔍 [bold]Checking environment variables...[/bold]")
    
    required_vars = {
        'PROJECT_ENDPOINT': 'Azure AI Foundry project endpoint',
        'MODEL_DEPLOYMENT_NAME': 'Model deployment name (e.g., gpt-4o-mini)',
        'AZURE_SUBSCRIPTION_ID': 'Azure subscription ID',
        'PROJECT_NAME': 'Azure AI Foundry project name'
    }
    
    env_table = Table()
    env_table.add_column("Variable", style="cyan")
    env_table.add_column("Status", style="green")
    env_table.add_column("Value Preview", style="dim")
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Show first 20 chars + ... for security
            preview = value[:20] + "..." if len(value) > 20 else value
            env_table.add_row(var, "✅ Set", preview)
        else:
            env_table.add_row(var, "❌ Missing", "Not set")
            success = False
    
    console.print(env_table)
    
    if not success:
        console.print("\n❌ [bold red]Environment variables missing![/bold red]")
        console.print("Please review the setup guide and configure missing variables.")
        return False
    
    # Test Azure authentication
    console.print("\n🔐 [bold]Testing Azure authentication...[/bold]")
    try:
        credential = DefaultAzureCredential()
        # Get a token to verify authentication works
        token = credential.get_token("https://management.azure.com/.default")
        console.print("✅ Azure authentication successful")
    except Exception as e:
        console.print(f"❌ Azure authentication failed: {e}")
        console.print("💡 Try running 'az login' to authenticate")
        return False
    
    # Test Azure AI Project connection
    console.print("\n🤖 [bold]Testing Azure AI Project connection...[/bold]")
    try:
        client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential()
        )
        
        # List deployments to verify connection
        deployments = list(client.deployments.list())
        console.print(f"✅ Connected to Azure AI Project successfully")
        console.print(f"✅ Found {len(deployments)} model deployments")
        
        # Display available deployments
        if deployments:
            deploy_table = Table()
            deploy_table.add_column("Deployment Name", style="cyan")
            deploy_table.add_column("Model Name", style="green")
            deploy_table.add_column("Status", style="yellow")
            
            for deployment in deployments:
                status = getattr(deployment, 'provisioning_state', 'Unknown')
                deploy_table.add_row(
                    deployment.name,
                    getattr(deployment, 'model_name', 'Unknown'),
                    status
                )
            
            console.print("\n📋 [bold]Available Deployments:[/bold]")
            console.print(deploy_table)
        
        # Check if our target model is deployed
        target_model = os.getenv('MODEL_DEPLOYMENT_NAME')
        model_found = any(d.name == target_model for d in deployments)
        
        if model_found:
            console.print(f"\n✅ Target model '{target_model}' found and accessible")
        else:
            console.print(f"\n⚠️  Target model '{target_model}' not found")
            if deployments:
                console.print("Available models:")
                for d in deployments:
                    console.print(f"   - {d.name}")
            console.print("💡 Deploy the required model in Azure AI Foundry portal")
    
    except Exception as e:
        console.print(f"❌ Azure AI Project connection failed: {str(e)[:100]}...")
        console.print("💡 Check your PROJECT_ENDPOINT and ensure it's correctly formatted")
        return False
    
    # Test basic agent operations
    console.print("\n🎯 [bold]Testing basic agent operations...[/bold]")
    try:
        # Just try to list agents (even if empty)
        agents_client = client.agents
        agents = list(agents_client.list_agents(limit=1))
        console.print(f"✅ Agent operations accessible ({len(agents)} existing agents)")
    except Exception as e:
        console.print(f"❌ Agent operations failed: {str(e)[:100]}...")
        return False
    
    # Success summary
    console.print(Panel.fit(
        "🎉 Setup validation completed successfully!\n"
        "Your environment is ready for Azure AI Foundry agent development.\n\n"
        "Next: Create your first agent with exercise_2_basic_agent.py",
        style="bold green",
        title="✅ SUCCESS"
    ))
    
    return True

def print_help():
    """Print helpful information for common issues"""
    console.print(Panel(
        "🆘 [bold]Common Issues & Solutions:[/bold]\n\n"
        "1. Authentication Failed:\n"
        "   • Run 'az login' to authenticate\n"
        "   • Verify subscription access with 'az account show'\n\n"
        "2. Project Connection Failed:\n"
        "   • Check PROJECT_ENDPOINT format\n"
        "   • Ensure you have 'Azure AI User' role\n\n"
        "3. Model Not Found:\n"
        "   • Deploy gpt-4o-mini model in Azure AI Foundry portal\n"
        "   • Update MODEL_DEPLOYMENT_NAME in .env\n\n"
        "4. Environment Variables Missing:\n"
        "   • Copy .env.template to .env\n"
        "   • Fill in all required values",
        title="💡 Help"
    ))

if __name__ == "__main__":
    try:
        success = asyncio.run(validate_setup())
        if not success:
            print_help()
    except KeyboardInterrupt:
        console.print("\n👋 Validation cancelled by user")
    except Exception as e:
        console.print(f"\n💥 [bold red]Unexpected error:[/bold red] {e}")
        print_help()
