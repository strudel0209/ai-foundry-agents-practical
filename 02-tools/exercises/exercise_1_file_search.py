#!/usr/bin/env python3

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FileSearchTool, FilePurpose


class DocumentProcessor:
    def __init__(self):
        load_dotenv()
        self.client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential(),
            api_version="2025-05-15-preview"
        )
        self.vector_store = None
        self.agent = None
        self.uploaded_files = []  # Track uploaded files for cleanup

    def create_sample_documents(self):
        """Create sample documents for testing"""
        docs_dir = Path("sample_docs")
        docs_dir.mkdir(exist_ok=True)
        
        documents = {
            "company_policy.txt": """
REMOTE WORK POLICY

Effective Date: January 1, 2025

1. ELIGIBILITY
All full-time employees are eligible for remote work after 90 days of employment.

2. EQUIPMENT
- Company provides laptop and software
- Employees responsible for internet connectivity
- VPN access required for all systems

3. WORK HOURS
- Core hours: 9 AM - 3 PM local time
- Flexible start/end times within 7 AM - 7 PM
- Minimum 8 hours per day required

4. COMMUNICATION
- Daily check-in with supervisor
- Weekly team meetings via video
- Response to messages within 4 hours during work hours

5. PERFORMANCE
- Same productivity standards as office workers
- Regular performance reviews
- Goal-based evaluation metrics
""",
            "technical_manual.txt": """
API INTEGRATION MANUAL

Version 2.1 - Updated January 2025

OVERVIEW
Comprehensive guidance for integrating with our REST API platform.

AUTHENTICATION
Base URL: https://api.company.com/v2
Authentication: Bearer token required
Rate Limits: 1000 requests/hour

ENDPOINTS

1. GET /users
   - Retrieve user information
   - Response: JSON user object

2. POST /documents
   - Upload document for processing
   - Max size: 10MB

3. GET /analytics
   - Retrieve usage analytics
   - Response: JSON analytics data

ERROR HANDLING
- 400: Bad Request
- 401: Unauthorized
- 429: Rate Limited
- 500: Server Error

BEST PRACTICES
- Implement exponential backoff
- Cache responses when possible
- Use webhook notifications
- Monitor API usage
""",
            "contract.txt": """
SERVICE AGREEMENT

Date: January 1, 2025
Parties: TechCorp Inc. and DataSolutions LLC

TERMS
- Service Period: 12 months
- Monthly Fee: $50,000
- SLA: 99.9% uptime
- Data Processing: GDPR compliant
- Termination: 30-day notice required

SERVICES
1. Cloud infrastructure management
2. Data backup and recovery
3. Security monitoring
4. Technical support (24/7)

CONTACTS
- TechCorp: contracts@techcorp.com
- DataSolutions: legal@datasolutions.com
"""
        }
        
        for filename, content in documents.items():
            filepath = docs_dir / filename
            filepath.write_text(content.strip())
        
        print(f"Created {len(documents)} sample documents in {docs_dir}")
        return list(docs_dir.glob("*.txt"))

    def upload_documents(self, file_paths):
        """Upload documents and create or reuse vector store"""
        print("Uploading documents...")

        uploaded_files = []
        for file_path in file_paths:
            # Upload file using the correct SDK method
            file_obj = self.client.agents.files.upload_and_poll(
                file_path=str(file_path),
                purpose=FilePurpose.AGENTS
            )
            uploaded_files.append(file_obj)
            self.uploaded_files.append(file_obj)  # Track for cleanup
            print(f"Uploaded: {file_path.name} -> {file_obj.id}")

        uploaded_file_ids = set(f.id for f in uploaded_files)

        # Check for existing vector store with the same files
        print("Checking for existing vector stores with the same files...")
        try:
            for vs in self.client.agents.vector_stores.list():
                # Get file IDs for this vector store
                vs_file_ids = set()
                try:
                    for f in self.client.agents.files.list(vector_store_id=vs.id):
                        vs_file_ids.add(f.id)
                except Exception as e:
                    print(f"Could not list files for vector store {vs.id}: {e}")
                    continue

                if vs_file_ids == uploaded_file_ids:
                    print(f"Found existing vector store: {vs.id}")
                    self.vector_store = vs
                    return self.vector_store
        except Exception as e:
            print(f"Error listing vector stores: {e}")

        # Create vector store using the correct SDK method
        self.vector_store = self.client.agents.vector_stores.create_and_poll(
            file_ids=[f.id for f in uploaded_files],
            name="document-intelligence-store"
        )

        print(f"Created vector store: {self.vector_store.id}")
        return self.vector_store

    def get_or_create_agent(self, name, model, instructions, tools, tool_resources):
        """Get existing agent or create new one"""
        try:
            agents = self.client.agents.list_agents()
            for agent in agents:
                if agent.name == name:
                    print(f"Found existing agent: {agent.id}")
                    return agent
        except Exception as e:
            print(f"Error listing agents: {e}")
        
        # Create new agent if none found
        agent = self.client.agents.create_agent(
            model=model,
            name=name,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources
        )
        print(f"Created new agent: {agent.id}")
        return agent
    
    def create_search_agent(self):
        """Create agent with file search capability"""
        file_search_tool = FileSearchTool(
            vector_store_ids=[self.vector_store.id]
        )
        
        self.agent = self.get_or_create_agent(
            name="document-search-agent",
            model=os.getenv('MODEL_DEPLOYMENT_NAME'),
            instructions="""
You are a document intelligence assistant. You help users find and analyze information from uploaded documents.

When answering questions:
1. Search through the available documents
2. Provide specific quotes and references
3. Cite the source document
4. Offer additional context when helpful
5. If information isn't found, say so clearly
""",
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources
        )
        
        print(f"Using search agent: {self.agent.id}")
        return self.agent

    def search_documents(self, query):
        """Search documents using the agent"""
        # Create thread for this search
        thread = self.client.agents.threads.create()
        
        # Send query
        self.client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )
        
        # Process with agent
        run = self.client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=self.agent.id
        )
        
        try:
            if run.status == "completed":
                messages = list(self.client.agents.messages.list(thread_id=thread.id))
                response = messages[0].content[0].text.value
                
                # Extract citations if present
                citations = []
                if hasattr(messages[0].content[0], 'annotations'):
                    for annotation in messages[0].content[0].annotations:
                        if hasattr(annotation, 'file_citation'):
                            citations.append(annotation.file_citation.file_id)
                
                return {
                    'response': response,
                    'citations': citations,
                    'status': 'success'
                }
            else:
                return {
                    'response': f"Search failed: {run.status}",
                    'citations': [],
                    'status': 'error'
                }
        except Exception as e:
            return {
                'response': f"Error during search: {str(e)}",
                'citations': [],
                'status': 'error'
            }
        # finally:
        #     # Always cleanup thread
        #     try:
        #         self.client.agents.threads.delete(thread.id)
        #     except Exception as e:
        #         print(f"Error deleting thread {thread.id}: {e}")

# def cleanup(self):
#     """Clean up resources"""
#     if self.agent:
#         self.client.agents.delete_agent(self.agent.id)
#         print(f"Deleted agent: {self.agent.id}")
    
#     if self.vector_store:
#         self.client.agents.delete_vector_store(self.vector_store.id)
#         print(f"Deleted vector store: {self.vector_store.id}")
    
#     # Clean up uploaded files
#     for file_obj in self.uploaded_files:
#         try:
#             self.client.agents.delete_file(file_obj.id)
#             print(f"Deleted file: {file_obj.id}")
#         except Exception as e:
#             print(f"Error deleting file {file_obj.id}: {e}")
    
#     self.uploaded_files.clear()

def run_file_search_demo():
    """Demonstrate file search capabilities"""
    print("🔍 Starting File Search Demo")
    print("=" * 40)
    
    processor = DocumentProcessor()
    
    try:
        # Setup
        file_paths = processor.create_sample_documents()
        processor.upload_documents(file_paths)
        processor.create_search_agent()
        
        # Test searches
        test_queries = [
            "What are the core work hours in the remote work policy?",
            "What is the API rate limit for our service?",
            "Who are the parties in the service agreement?",
            "What are the best practices for API integration?",
            "What is the monthly fee in the contract?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Search {i} ---")
            print(f"Query: {query}")
            
            result = processor.search_documents(query)
            if result['status'] == 'success':
                print(f"Response: {result['response'][:200]}...")
                if result['citations']:
                    print(f"Citations: {len(result['citations'])} documents referenced")
            else:
                print(f"Error: {result['response']}")
        
        print("\n✅ File search demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    # finally:
    #     processor.cleanup()


if __name__ == "__main__":
    run_file_search_demo()
