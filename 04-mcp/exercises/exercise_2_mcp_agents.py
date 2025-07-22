"""
Exercise 2: Azure AI Foundry Agent with SQLite MCP Server Integration

This exercise demonstrates how to connect an Azure AI Foundry agent
to a SQLite database through the Model Context Protocol (MCP).
"""

import time
import json
import os
import requests
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000")

def check_mcp_url():
    """Check if MCP server URL is publicly accessible"""
    if "localhost" in MCP_SERVER_URL or "127.0.0.1" in MCP_SERVER_URL:
        print("\n⚠️  WARNING: MCP server URL is set to localhost!")
        print("   Azure agents CANNOT access localhost URLs.")
        print("\n   To fix this, you need to expose your MCP server publicly:")
        print("\n   Option 1 - Deploy to Azure Container Apps (recommended):")
        print("   1. Make the deployment script executable:")
        print("      chmod +x deploy-mcp-to-container-apps.sh")
        print("   2. Run the deployment:")
        print("      ./deploy-mcp-to-container-apps.sh")
        print("   3. Update .env with the provided URL")
        print("\n   Option 2 - Use ngrok (for testing only):")
        print("   1. Install ngrok: https://ngrok.com/download")
        print("   2. Run: ngrok http 3000")
        print("   3. Copy the public URL (e.g., https://abc123.ngrok.io)")
        print("   4. Update .env: MCP_SERVER_URL=https://abc123.ngrok.io")
        print("\n" + "="*60)
        return False
    
    # Check if it's a valid public URL
    if MCP_SERVER_URL.startswith("https://") or MCP_SERVER_URL.startswith("http://"):
        print(f"✅ MCP Server URL is configured: {MCP_SERVER_URL}")
        return True
    else:
        print(f"⚠️  Invalid MCP Server URL format: {MCP_SERVER_URL}")
        print("   URL should start with http:// or https://")
        return False

def create_mcp_agent_with_sqlite():
    """Create an Azure AI Foundry agent with SQLite MCP integration for business analytics"""
    
    # Create AI Project Client
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )

    with project_client:
        try:
            # Create agent with native MCP tool configuration
            agent = project_client.agents.create_agent(
                model=os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'), 
                name="business-analytics-agent", 
                instructions="""You are a business analytics expert with direct access to the company database through SQL queries.
                
                You have access to a business database with the following tables:
                - customers: customer information (id, name, email, phone, address, city, state, country, postal_code)
                - products: product catalog (id, name, category, price, stock_quantity)
                - orders: order records (id, customer_id, order_date, total_amount, status)
                - order_items: order details (id, order_id, product_id, quantity, unit_price, total_price)
                
                You can help with:
                - Financial analysis and revenue trends
                - Product performance and inventory analysis
                - Customer analytics and segmentation
                - Sales patterns by region and time
                - Order status and fulfillment metrics
                
                When analyzing data:
                1. Use SQL queries to retrieve relevant data
                2. Provide clear insights and actionable recommendations
                3. Calculate business metrics (growth rates, margins, etc.)
                4. Identify trends and patterns
                5. Suggest appropriate visualizations
                
                Always verify your queries work correctly and handle any errors gracefully.""",
                tools=[
                    {
                        "type": "mcp",
                        "server_label": "sqlite_business",  # <-- FIXED: only letters, numbers, underscores
                        "server_url": MCP_SERVER_URL,
                        "allowed_tools": ["sql_query", "list_tables", "table_schema"]
                    }
                ]
            )
            print(f"✅ Created business analytics agent: {agent.id}")
        except Exception as e:
            print(f"❌ Failed to create agent: {e}")
            if "invalid_engine_error" in str(e) or "Failed to resolve model info" in str(e):
                print("\n⚠️  Model deployment error detected!")
                print("   Ensure your model is deployed in a supported region")
                print("   Current deployment name:", os.getenv('MODEL_DEPLOYMENT_NAME'))
            raise

        # Create a thread
        thread = project_client.agents.threads.create()
        print(f"📞 Created thread: {thread.id}")

        # Real business analytics scenarios using actual database
        analytics_scenarios = [
            {
                "title": "Revenue Analysis by Product Category",
                "query": """Analyze our revenue by product category. 
                Show me the total revenue for each product category and identify the top performing categories."""
            },
            {
                "title": "Customer Order Patterns",
                "query": """Analyze customer ordering patterns. 
                Show me customers with the most orders, average order values, and identify our VIP customers."""
            },
            {
                "title": "Product Inventory Status",
                "query": """Check our current inventory status.
                Show me products with low stock (less than 20 units) and calculate the total inventory value."""
            },
            {
                "title": "Sales Trends Over Time",
                "query": """Analyze our sales trends over the past months.
                Show me monthly revenue, number of orders, and identify any seasonal patterns."""
            }
        ]

        for scenario in analytics_scenarios:
            print(f"\n📊 {scenario['title']}")
            print("=" * 60)
            
            # Send analytics request
            message = project_client.agents.messages.create(
                thread_id=thread.id, 
                role="user", 
                content=scenario['query'],
            )
            print(f"📤 Analyzing business data...")

            try:
                # Create run with detailed error handling
                run = project_client.agents.runs.create(
                    thread_id=thread.id, 
                    agent_id=agent.id,
                    tool_resources={
                        "mcp": [
                            {
                                "server_label": "sqlite_business",
                                # No headers, no auth token
                                "require_approval": "never"
                            }
                        ]
                    },
                    metadata={
                        "scenario": scenario['title'],
                        "mcp_enabled": "true"
                    }
                )
                
                # Poll for completion with timeout
                max_attempts = 60  # 60 seconds timeout
                attempts = 0
                
                while run.status in ["queued", "in_progress", "requires_action"] and attempts < max_attempts:
                    time.sleep(1)
                    attempts += 1
                    run = project_client.agents.runs.get(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    
                    # Handle requires_action status for MCP approval
                    if run.status == "requires_action":
                        print(f"   ⚠️  Action required: {run.required_action}")
                        # In production, you would handle approval here
                        # For now, we set require_approval to "never" above
                    
                    # Print status updates for debugging
                    if attempts % 5 == 0:
                        print(f"   Status: {run.status} (attempt {attempts}/{max_attempts})")
                
                if run.status == "failed":
                    print(f"❌ Analysis failed: {run.last_error}")
                    
                    # Enhanced error diagnostics
                    if run.last_error and isinstance(run.last_error, dict):
                        error_code = run.last_error.get('code', '')
                        error_msg = run.last_error.get('message', '')
                        
                        if error_code == 'server_error' and 'Sorry, something went wrong' in error_msg:
                            print("\n🔍 Diagnostics for 'server_error':")
                            print("   1. Check if MCP server is responding correctly")
                            print("   2. Verify the MCP protocol version matches Azure AI expectations")
                            print("   3. Ensure CORS headers are properly configured")
                            print("   4. Check Azure Container Apps logs for server errors")
                            print("\n   Testing MCP server directly...")
                            
                            # Test MCP server capabilities
                            test_mcp_capabilities()
                    
                    continue
                elif run.status == "completed":
                    print(f"✅ Analysis completed successfully")
                else:
                    print(f"⚠️  Unexpected run status: {run.status}")

            except Exception as e:
                print(f"❌ Error during run execution: {e}")
                print(f"   Error type: {type(e).__name__}")
                continue

            # Get the response
            messages = project_client.agents.messages.list(thread_id=thread.id)
            
            # Find and display the assistant's analysis
            for msg in messages:
                if msg.role == "assistant" and msg.created_at > message.created_at:
                    for content in msg.content:
                        if hasattr(content, 'text') and hasattr(content.text, 'value'):
                            print(f"\n💡 Analysis Results:")
                            print(content.text.value)
                            break
                    break
            
            print("\n" + "-" * 60)

def test_mcp_connection():
    """Test the MCP server connection"""
    print(f"\n🔍 Testing MCP Server Connection at {MCP_SERVER_URL}")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ MCP Server is healthy: {response.json()}")
            return True
        else:
            print(f"❌ MCP Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to MCP Server: {e}")
        return False

def test_mcp_capabilities():
    """Test MCP server capabilities endpoint"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/capabilities", timeout=5)
        if response.status_code == 200:
            print(f"✅ MCP Server capabilities: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ Failed to get MCP capabilities: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting MCP capabilities: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Azure AI Foundry + MCP Business Analytics Demo")
    print("=" * 60)
    
    # Check MCP URL first
    if not check_mcp_url():
        print("\n❌ Please fix the MCP server URL issue before continuing.")
        print("\n💡 Quick fix options:")
        print("1. Deploy to Azure (recommended): ./deploy-mcp-to-container-apps.sh")
        print("2. Use ngrok for testing: ngrok http 3000")
        exit(1)
    
    # Test MCP connection first
    if not test_mcp_connection():
        print("\n⚠️  MCP server is not accessible!")
        print("   Check the Azure Container Apps logs:")
        print(f"   az containerapp logs show -n mcp-sqlite-server -g {os.getenv('AZURE_RESOURCE_GROUP')}")
        exit(1)
    
    print("\n💼 Running Business Analytics Agent Demo")
    print("\nThe agent will query real business data from the SQLite database via MCP.\n")
    
    try:
        create_mcp_agent_with_sqlite()
        print("\n✅ Business analytics demo completed successfully!")
        
        print("\n📝 Key Features of Native MCP Support:")
        print("1. Direct MCP tool configuration with server_label")
        print("2. Automatic tool discovery from MCP server")
        print("3. Built-in approval workflows (always/never/selective)")
        print("4. Headers passed via tool_resources at runtime")
        print("5. Seamless integration with Azure AI Foundry agents")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check Container Apps logs: az containerapp logs show -n mcp-sqlite-server -g rg-multi-agents")
        print("2. Verify MCP server is running: curl https://mcp-sqlite-server.grayflower-3ce4933b.westus2.azurecontainerapps.io/health")
        print("3. Ensure Azure AI Foundry region supports MCP tools")
        print("4. Check that your model deployment exists and is accessible")