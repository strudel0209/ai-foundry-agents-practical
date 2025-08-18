#!/usr/bin/env python3
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import SharepointTool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SharePointDemo:
    def __init__(self):
        """Initialize the SharePoint Demo with Azure AI Foundry client"""
        # Validate required environment variables
        required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME", "SHAREPOINT_CONNECTION_NAME"]
        for var in required_vars:
            if not os.getenv(var):
                raise EnvironmentError(f"Missing required environment variable: {var}")
        
        # Initialize the AIProjectClient
        self.project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential(),
        )
        
        self.agent = None
        self.thread = None
    
    def setup_sharepoint_tool(self):
        """Setup SharePoint tool with the connection"""
        try:
            connection_name = os.environ["SHAREPOINT_CONNECTION_NAME"]
            
            conn = self.project_client.connections.get(name=connection_name)
            print(f"✅ Found SharePoint connection: {conn.id}")
            
            # Initialize SharePoint tool with connection id
            sharepoint = SharepointTool(connection_id=conn.id)
            return sharepoint
            
        except Exception as e:
            print(f"❌ Error getting SharePoint connection: {e}")
            raise
    
    def create_agent(self):
        """Create an agent with SharePoint tool"""
        sharepoint = self.setup_sharepoint_tool()
        
        # Create agent with more specific SharePoint instructions
        self.agent = self.project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="sharepoint-demo-agent",
            instructions="""You are a helpful assistant with access to SharePoint documents.
            
            IMPORTANT: When users ask about documents:
            1. Always use the SharePoint tool to search for documents
            2. Try different search queries if the first doesn't return results
            3. Search for file types like PDF, DOCX, etc.
            4. If no results, try searching with broader terms or wildcards
            
            The SharePoint site contains documents in a 'docs' folder with PDF files.
            Always attempt to retrieve and summarize information from these documents.""",
            tools=sharepoint.definitions
        )
        print(f"✅ Created agent with SharePoint tool, ID: {self.agent.id}")
        return self.agent
    
    def run_query(self, query):
        """Run a query with the SharePoint agent"""
        if not self.agent:
            self.create_agent()
        
        # Create thread
        self.thread = self.project_client.agents.threads.create()
        print(f"📝 Created thread, ID: {self.thread.id}")
        
        # Create message
        message = self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=query
        )
        print(f"💬 Created message, ID: {message.id}")
        
        # Create and process run
        print("🔄 Processing query...")
        run = self.project_client.agents.runs.create_and_process(
            thread_id=self.thread.id,
            agent_id=self.agent.id
        )
        
        print(f"✅ Run finished with status: {run.status}")
        
        if run.status == "failed":
            print(f"❌ Run failed: {run.last_error}")
            return None
        
        # Fetch and display messages
        messages = self.project_client.agents.messages.list(thread_id=self.thread.id)
        print("\n📋 Conversation:")
        print("-" * 40)
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role.upper()}: {last_text.text.value}\n")
        
        return messages
    
    # def cleanup(self):
    #     """Clean up resources"""
    #     if self.agent:
    #         try:
    #             self.project_client.agents.delete_agent(self.agent.id)
    #             print(f"🗑️ Deleted agent: {self.agent.id}")
    #         except Exception as e:
    #             print(f"Error deleting agent: {e}")


def run_sharepoint_demo():
    """Demonstrate SharePoint tool capabilities"""
    print("📂 SharePoint Tool Demo")
    print("=" * 40)
    
    demo = SharePointDemo()
    
    try:
        # Create agent with SharePoint tool
        demo.create_agent()
        
        # Test queries
        queries = [
            "What documents are available in the SharePoint site?",
            "Summarize the key points from the employee handbook if available",
            "Find information about company policies"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: {query}")
            print("-" * 40)
            demo.run_query(query)
            
    except Exception as e:
        print(f"\n❌ Error running SharePoint demo: {e}")

    finally:
        # Uncomment to clean up
        # demo.cleanup()
        pass


if __name__ == "__main__":
    run_sharepoint_demo()