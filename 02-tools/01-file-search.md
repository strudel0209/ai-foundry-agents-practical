# 1. File Search Tool - Vector-Based Document Intelligence

In this lesson, you'll master the File Search tool - one of the most powerful capabilities in Azure AI Foundry for building document intelligence systems. This tool enables semantic search across your documents using vector embeddings.

## 🎯 Objectives

- Understand vector-based document search concepts
- Upload and index documents for search
- Create agents with File Search capabilities
- Build document processing workflows
- Implement enterprise document intelligence patterns

## ⏱️ Estimated Time: 60 minutes

## 🧠 Key Concepts

### What is File Search?

File Search is a Retrieval-Augmented Generation (RAG) tool that:
- **Indexes documents** using vector embeddings
- **Chunks content** into searchable segments  
- **Ranks results** by semantic relevance
- **Provides citations** with source references
- **Supports multiple formats** (PDF, TXT, DOCX, etc.)

### Vector Search Architecture

```
Document Upload → Chunking → Embedding → Vector Store → Search Index
                                                           ↓
User Query → Query Embedding → Similarity Search → Ranked Results
```

### Key Components

1. **Vector Store**: A vector store is a managed, cloud-based container that stores vector embeddings and metadata for your uploaded documents. When you upload files, the system splits them into chunks, generates vector embeddings for each chunk, and stores both the embeddings and references to the original files in the vector store. This enables fast, semantic similarity search across all indexed content. In Azure AI Foundry, vector stores are persistent, reusable, and can be shared across multiple agents or assistants. They are not local files, but are managed by the Azure AI Projects service in the cloud.
2. **File Objects**: Uploaded documents in various formats
3. **Embeddings**: Vector representations of text chunks
4. **Search Tool**: Interface for semantic queries

## 🚀 Step-by-Step Implementation

def upload_and_index_documents():
def create_sample_document(filename: str):

### Step 1: File Upload and Vector Store Reuse

```python
# exercises/exercise_1_file_search.py
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FileSearchTool, FilePurpose
from azure.identity import DefaultAzureCredential


    """Upload documents and create or reuse vector store for search"""
    load_dotenv()
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )

    # Step 1: Upload sample documents
    sample_files = [
        "company_policy.txt",
        "technical_manual.txt",
        "contract.txt"
    ]

    uploaded_files = []
    for file_path in sample_files:
        # Create sample file if it doesn't exist
        if not Path(file_path).exists():
            create_sample_document(file_path)
        try:
            file_obj = project_client.agents.files.upload_and_poll(
                file_path=file_path,
                purpose=FilePurpose.AGENTS
            )
            uploaded_files.append(file_obj)
            print(f"✅ Uploaded: {file_path} (ID: {file_obj.id})")
        except Exception as e:
            print(f"❌ Failed to upload {file_path}: {e}")

    if not uploaded_files:
        print("❌ No files uploaded successfully")
        return None, None

    uploaded_file_ids = set(f.id for f in uploaded_files)

    # Step 2: Check for existing vector store with the same files
    print("🔍 Checking for existing vector stores with the same files...")
    try:
        for vs in project_client.agents.vector_stores.list():
            vs_file_ids = set()
            try:
                for f in project_client.agents.files.list(vector_store_id=vs.id):
                    vs_file_ids.add(f.id)
            except Exception as e:
                print(f"Could not list files for vector store {vs.id}: {e}")
                continue
            if vs_file_ids == uploaded_file_ids:
                print(f"Found existing vector store: {vs.id}")
                return vs, uploaded_files
    except Exception as e:
        print(f"Error listing vector stores: {e}")

    # Step 3: Create vector store if not found
    vector_store = project_client.agents.vector_stores.create_and_poll(
        file_ids=[f.id for f in uploaded_files],
        name="document-intelligence-store"
    )
    print(f"✅ Created vector store: {vector_store.id}")
    print(f"📊 Indexed {len(uploaded_files)} documents")
    return vector_store, uploaded_files

### Step 2: Creating Agent with File Search
    """Create sample documents for demonstration"""
    # ... (same as before, see previous content for details)
```

### Step 2: Creating Agent with File Search

```python
def create_file_search_agent(project_client, vector_store):
    """Create an agent with File Search capabilities"""
    
    console.print("\n🤖 Creating File Search Agent...")
    
    # Create File Search tool with the vector store
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
    
    # Create agent with file search capabilities
    agent = project_client.agents.create_agent(
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),
        name="document-intelligence-agent",
        instructions="""
        You are a professional document analysis assistant with expertise in:
        
        - Contract analysis and term extraction
        - Policy interpretation and compliance
        - Technical documentation review
        - Information synthesis across multiple documents
        
        When searching documents:
        1. Provide accurate information with specific citations
        2. Summarize key findings clearly
        3. Highlight important terms, dates, and requirements
        4. Cross-reference information across documents when relevant
        5. Flag any potential compliance or security concerns
        
        Always cite your sources and be precise about document references.
        """,
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources
    )
    
    console.print(f"✅ Created agent: {agent.id}")
    console.print(f"🔧 Enabled tools: File Search")
    console.print(f"📚 Vector stores: {len(file_search_tool.vector_store_ids)}")
    
    return agent, file_search_tool
```

### Step 3: Advanced Search Scenarios

```python
async def demonstrate_search_scenarios(project_client, agent):
    """Demonstrate various document search scenarios"""
    
    console.print(Panel.fit(
        "🔍 Document Search Scenarios",
        style="bold green"
    ))
    
    # Search scenarios for our business use case
    search_scenarios = [
        {
            "name": "Contract Analysis",
            "query": "What are the key financial terms and obligations in the service agreement? Include payment amounts, duration, and termination clauses.",
            "expected": "Should find contract details, $50,000 monthly fee, 12-month period"
        },
        {
            "name": "Policy Compliance", 
            "query": "What are the remote work equipment requirements and who is responsible for what?",
            "expected": "Should find equipment policy, company provides laptop, employee handles internet"
        },
        {
            "name": "Technical Integration",
            "query": "How do I authenticate with the API and what are the rate limits?",
            "expected": "Should find Bearer token auth, 1000 requests/hour limit"
        },
        {
            "name": "Cross-Document Analysis",
            "query": "Are there any security or compliance requirements mentioned across all documents?",
            "expected": "Should find GDPR compliance, VPN requirements, security training"
        },
        {
            "name": "Specific Information Extraction",
            "query": "List all contact information and support channels mentioned in the documents.",
            "expected": "Should find email addresses, support channels, documentation links"
        }
    ]
    
    for i, scenario in enumerate(search_scenarios, 1):
        console.print(f"\n📋 [bold]Scenario {i}: {scenario['name']}[/bold]")
        console.print(f"🔍 Query: [dim]{scenario['query']}[/dim]")
        console.print(f"💡 Expected: [dim]{scenario['expected']}[/dim]")
        
        # Create thread and execute search
        thread = project_client.agents.create_thread()
        
        # Add user message
        project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=scenario['query']
        )
        
        # Run agent
        run = project_client.agents.create_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Wait for completion
        while True:
            run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
            if run.status in ["completed", "failed", "cancelled", "expired"]:
                break
            await asyncio.sleep(1)
        
        # Get response
        if run.status == "completed":
            messages = project_client.agents.list_messages(thread_id=thread.id)
            
            # Find the assistant's response
            for message in messages.data:
                if message.role == "assistant":
                    response_content = message.content[0].text.value if message.content else "No response"
                    console.print(f"🤖 [green]Agent Response:[/green]")
                    console.print(Panel(response_content, border_style="green"))
                    break
        else:
            console.print(f"❌ Run failed with status: {run.status}")
        
        console.print("\n" + "─" * 60)
```

### Step 4: Enterprise File Search Patterns

```python
class DocumentIntelligenceSystem:
    """Enterprise-grade document intelligence system"""
    
    def __init__(self, project_client):
        self.client = project_client
        self.vector_stores = {}
        self.agents = {}
        
    def create_specialized_stores(self):
        """Create specialized vector stores for different document types"""
        
        store_configs = {
            "contracts": {
                "name": "legal-contracts-store",
                "description": "Legal contracts and agreements"
            },
            "policies": {
                "name": "company-policies-store", 
                "description": "Internal policies and procedures"
            },
            "technical": {
                "name": "technical-docs-store",
                "description": "Technical manuals and documentation"
            }
        }
        
        for store_type, config in store_configs.items():
            vector_store = self.client.agents.vector_stores.create_and_poll(
                name=config["name"],
                file_ids=[]  # Start empty, add files as needed
            )
            
            self.vector_stores[store_type] = vector_store
            console.print(f"✅ Created {store_type} store: {vector_store.id}")
    
    def create_specialized_agents(self):
        """Create specialized agents for different document types"""
        
        agent_configs = {
            "contract_analyzer": {
                "name": "contract-analysis-specialist",
                "instructions": """
                You are a legal contract analysis specialist. Focus on:
                - Financial terms and obligations
                - Key dates and deadlines
                - Termination and renewal clauses
                - Compliance requirements
                - Risk assessment
                
                Provide structured analysis with clear section references.
                """,
                "store_type": "contracts"
            },
            "policy_advisor": {
                "name": "policy-compliance-advisor", 
                "instructions": """
                You are a company policy and compliance advisor. Focus on:
                - Policy requirements and procedures
                - Compliance obligations
                - Employee responsibilities
                - Approval workflows
                - Exception handling
                
                Provide clear guidance on policy compliance.
                """,
                "store_type": "policies"
            },
            "technical_consultant": {
                "name": "technical-documentation-consultant",
                "instructions": """
                You are a technical documentation specialist. Focus on:
                - API specifications and usage
                - Integration procedures
                - Technical requirements
                - Troubleshooting guidance
                - Best practices
                
                Provide detailed technical guidance with examples.
                """,
                "store_type": "technical"
            }
        }
        
        for agent_type, config in agent_configs.items():
            vector_store = self.vector_stores[config["store_type"]]
            file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
            
            agent = self.client.agents.create_agent(
                model=os.getenv('MODEL_DEPLOYMENT_NAME'),
                name=config["name"],
                instructions=config["instructions"],
                tools=file_search_tool.definitions,
                tool_resources=file_search_tool.resources
            )
            
            self.agents[agent_type] = agent
            console.print(f"🤖 Created {agent_type}: {agent.id}")
    
    def route_query(self, query: str) -> str:
        """Intelligent query routing to appropriate specialist agent"""
        
        # Simple keyword-based routing (can be enhanced with ML)
        routing_keywords = {
            "contract_analyzer": ["contract", "agreement", "payment", "fee", "termination", "legal"],
            "policy_advisor": ["policy", "remote work", "employee", "compliance", "procedure"],
            "technical_consultant": ["api", "integration", "technical", "authentication", "endpoint"]
        }
        
        query_lower = query.lower()
        scores = {}
        
        for agent_type, keywords in routing_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            scores[agent_type] = score
        
        # Return agent with highest score
        best_agent = max(scores, key=scores.get)
        return best_agent if scores[best_agent] > 0 else "contract_analyzer"  # Default
    
    async def process_query(self, query: str):
        """Process query with appropriate specialist agent"""
        
        # Route to best agent
        agent_type = self.route_query(query)
        agent = self.agents[agent_type]
        
        console.print(f"🎯 Routing to: [bold]{agent_type}[/bold]")
        
        # Create thread and process
        thread = self.client.agents.create_thread()
        
        self.client.agents.create_message(
            thread_id=thread.id,
            role="user", 
            content=query
        )
        
        run = self.client.agents.create_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # Wait for completion
        while True:
            run = self.client.agents.get_run(thread_id=thread.id, run_id=run.id)
            if run.status in ["completed", "failed", "cancelled", "expired"]:
                break
            await asyncio.sleep(1)
        
        # Return response
        if run.status == "completed":
            messages = self.client.agents.list_messages(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    return message.content[0].text.value if message.content else "No response"
        
        return f"Query processing failed: {run.status}"
```

## 🎯 Exercises

### Exercise A: Document Category Analysis

Build a system that automatically categorizes uploaded documents:

1. Upload 10 different document types
2. Create an agent that categorizes them
3. Extract key metadata from each category
4. Generate a summary report

### Exercise B: Multi-Language Document Search

Implement search across documents in different languages:

1. Upload documents in multiple languages
2. Test semantic search capabilities
3. Implement language-aware routing
4. Compare search quality across languages

### Exercise C: Real-Time Document Monitoring

Build a system that monitors document changes:

1. Implement document upload workflows
2. Track document updates and versions
3. Send notifications for important changes
4. Maintain search index consistency

## 🔍 Best Practices

### Vector Store Management

1. **Organize by Type**: Separate stores for different document categories
2. **Optimize Chunk Size**: Balance between context and granularity
3. **Monitor Performance**: Track search latency and relevance
4. **Regular Cleanup**: Remove outdated or duplicate documents

### Search Optimization

1. **Query Engineering**: The Azure file search tool and vector store APIs can automatically rewrite and optimize user queries for better retrieval. You can also pre-process queries in your application before sending them to the vector store. Use the `rewrite_query` parameter for automatic optimization.
2. **Result Ranking**: You can specify ranking options such as similarity metric, score threshold, and ranker (e.g., `auto` or a specific version) in your search request. Hybrid search and semantic ranking are also supported for improved relevance. Example:

   ```python
   search_results = client.agents.vector_stores.search(
       vector_store_id=vector_store.id,
       query="What are the core work hours in the remote work policy?",
       ranking_options={"score_threshold": 0.7, "ranker": "auto"},
       max_num_results=5,
       rewrite_query=True
   )
   ```
3. **Citation Tracking**: The file search tool automatically tracks and returns citations (source file references) for each result chunk. You can access these in the API response and display them to users.
4. **Result Filtering**: You can apply filters to vector search queries based on file metadata (e.g., document type, date, tags). Example:

   ```python
   search_results = client.agents.vector_stores.search(
       vector_store_id=vector_store.id,
       query="API authentication",
       filters={"fileType": "txt", "createdDate": {"gte": "2025-01-01"}}
   )
   ```

These options allow you to control and optimize search behavior through query parameters, ranking, and filtering, while leveraging the fully managed vector store. See the [Microsoft Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference-preview#search-vector-store) for more details and examples.

### Security & Compliance

1. **Access Control**: Implement document-level permissions
2. **Data Privacy**: Handle sensitive documents appropriately
3. **Audit Trails**: Log all document access and search activities
4. **Compliance**: Ensure GDPR/HIPAA compliance for regulated documents

## 🔧 Troubleshooting

### Common Issues

**File upload fails:**
- Check file size limits (32MB max)
- Verify supported formats (PDF, TXT, DOCX, etc.)
- Ensure proper authentication

**Search returns irrelevant results:**
- Review query phrasing and specificity
- Check document content quality
- Consider chunk size optimization

**Vector store creation slow:**
- Large documents take time to process
- Monitor indexing progress
- Consider batch processing

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Vector Search Concepts**: How semantic search works with embeddings
2. **File Management**: Uploading, indexing, and organizing documents
3. **Agent Integration**: Creating agents with file search capabilities
4. **Enterprise Patterns**: Building scalable document intelligence systems
5. **Performance Optimization**: Best practices for production systems

## ➡️ Next Step

Once you've mastered File Search, proceed to [Azure AI Search Tool](./02-azure-ai-search.md) to learn enterprise search capabilities.

---

**💡 Pro Tip**: File Search is most effective when combined with other tools. Use it for information retrieval, then apply Code Interpreter for analysis or Function Calling for business logic.
