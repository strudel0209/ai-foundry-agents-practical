"""
Advanced Semantic Kernel Integration with Azure AI Foundry Agents

This module demonstrates multi-agent orchestration using Semantic Kernel,implementing complex workflows and agent collaboration patterns.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, Annotated
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig
from semantic_kernel.functions import KernelFunction
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding


from semantic_kernel.connectors.azure_ai_search import AzureAISearchCollection
from semantic_kernel.connectors.in_memory import InMemoryCollection

from semantic_kernel.data.vector import (
    VectorStoreField,
    DistanceFunction,
    IndexKind,
    vectorstoremodel,
)

from azure.ai.projects import AIProjectClient, enable_telemetry
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SearchField, SearchFieldDataType, VectorSearch, VectorSearchProfile, HnswAlgorithmConfiguration
from azure.search.documents.aio import SearchClient
import uuid
from datetime import datetime

from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from azure.monitor.opentelemetry import configure_azure_monitor

# Data model for memory records
from dataclasses import dataclass
from typing import Optional as Opt

# Load environment variables
load_dotenv()

# === Tracing setup ===
# Set a consistent service name and enable content capture
os.environ.setdefault("OTEL_SERVICE_NAME", "sk-advanced-agents")
os.environ.setdefault("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")
# Enable Azure SDK/Agents telemetry hooks
try:
    enable_telemetry()
except Exception:
    pass

# Configure Azure Monitor exporter: prefer env; fallback to AI Project telemetry
try:
    _conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not _conn:
        # Prefer standard env var name; fall back to legacy if present
        _proj_ep = os.getenv("AZURE_AI_PROJECT_ENDPOINT") or os.getenv("PROJECT_ENDPOINT")
        if _proj_ep:
            try:
                _tmp = AIProjectClient(endpoint=_proj_ep, credential=DefaultAzureCredential())
                _conn = _tmp.telemetry.get_application_insights_connection_string()
            except Exception as e:
                print(f"⚠️ Unable to fetch Application Insights connection from project endpoint: {e}")
    if _conn:
        # Correct signature: only pass the connection string
        configure_azure_monitor(connection_string=_conn)
        LoggingInstrumentor().instrument(set_logging_format=True)
        print("✅ Azure Monitor tracing configured")
    else:
        print(
            "⚠️ No Application Insights connection string found."
        )
except Exception as e:
    # If config fails, traces will not be exported but app behavior remains unchanged
    print(f"⚠️ Azure Monitor tracing not configured: {e}")

# Get a tracer to annotate key flows with spans
_tracer = trace.get_tracer(__name__)

@vectorstoremodel(collection_name="agent_workflow_memory")
@dataclass
class WorkflowMemoryRecord:
    id: Annotated[str, VectorStoreField("key")]
    agent_name: Annotated[str, VectorStoreField("data", is_indexed=True)]
    request: Annotated[str, VectorStoreField("data", is_full_text_indexed=True)]
    response: Annotated[str, VectorStoreField("data", is_full_text_indexed=True)]
    context: Annotated[str, VectorStoreField("data")]
    timestamp: Annotated[str, VectorStoreField("data")]
    embedding: Annotated[
        list[float] | str | None,
        VectorStoreField(
            "vector",
            dimensions=1536,
            distance_function=DistanceFunction.COSINE_DISTANCE,
            index_kind=IndexKind.HNSW
        )
    ] = None

    def __post_init__(self):
        if self.embedding is None:
            self.embedding = f"{self.request} {self.response}"

class MultiAgentOrchestrator:
    """Orchestrates multiple Azure AI Foundry agents using Semantic Kernel"""
    
    def __init__(self, use_azure_search: bool = True):
        load_dotenv()
        print("DEBUG: AZURE_AI_SEARCH_ENDPOINT =", os.getenv('AZURE_AI_SEARCH_ENDPOINT'))
        print("DEBUG: AZURE_AI_SEARCH_API_KEY =", os.getenv('AZURE_AI_SEARCH_API_KEY'))
        
        # Initialize Semantic Kernel
        self.kernel = sk.Kernel()
        self._setup_semantic_kernel()
        
        # Initialize Azure AI Foundry client
        self.credential = DefaultAzureCredential()
        self.ai_client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=self.credential
        )
        
        # Agent registry
        self.agents = {}
        self.agent_capabilities = {}
        
        # Initialize vector store and memory
        self.use_azure_search = use_azure_search
        self.memory_collection = None
        self.embedding_service = None
        self._setup_memory_store()
        
    def _setup_semantic_kernel(self):
        """Configure Semantic Kernel with Azure OpenAI"""

        # Ensure deployment name matches the actual Azure OpenAI deployment
        deployment_name = os.getenv('MODEL_DEPLOYMENT_NAME', '').strip()
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').strip()
        api_key = os.getenv('AZURE_OPENAI_API_KEY', '').strip()
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2025-04-01-preview').strip()
        embedding_deployment_name = os.getenv('EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002').strip()

        # Validate critical environment variables
        if not endpoint or not api_key or not deployment_name:
            raise RuntimeError(
                "Azure OpenAI configuration missing. "
                "Check AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and MODEL_DEPLOYMENT_NAME in your .env file."
            )
            
        # Add Azure OpenAI chat completion service
        self.kernel.add_service(
            AzureChatCompletion(
                service_id="chat-gpt",
                deployment_name=deployment_name,
                endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        )

        self.kernel.add_service(
            AzureTextEmbedding(
                service_id="text-embedding",
                deployment_name=embedding_deployment_name,
                endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        )
        print("✅ Semantic Kernel configured with Azure OpenAI and embeddings")
    
    def _setup_memory_store(self):
        """Set up vector store for workflow context retention - Azure AI Search for production"""

        record_type = WorkflowMemoryRecord

        try:
            endpoint = os.getenv('AZURE_AI_SEARCH_ENDPOINT')
            api_key = os.getenv('AZURE_AI_SEARCH_API_KEY')
            # Only use Azure AI Search if BOTH endpoint and api_key are set and non-empty
            if self.use_azure_search and endpoint and api_key:
                print("🔍 Setting up Azure AI Search vector store...")

                # Ensure index exists synchronously before collection creation
                # This avoids event loop issues in __init__ context
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self._ensure_collection_exists())

                self.memory_collection = AzureAISearchCollection(
                    record_type=record_type,
                    collection_name="agent_workflow_memory",
                    url=endpoint,
                    api_key=api_key,
                )
                print("✅ Azure AI Search vector store initialized for production use")
            else:
                print("💾 Using in-memory vector store (development mode)")
                self.memory_collection = InMemoryCollection(
                    record_type=record_type,
                    collection_name="workflow_memory"
                )
                print("✅ In-memory vector store initialized for development")
        except Exception as e:
            print(f"⚠️ Failed to initialize vector store, falling back to in-memory: {e}")
            self.memory_collection = InMemoryCollection(
                record_type=record_type,
                collection_name="workflow_memory"
            )
    
    async def _ensure_collection_exists(self):
        """Ensure the Azure AI Search index exists"""
        try:
            endpoint = os.getenv('AZURE_AI_SEARCH_ENDPOINT')
            api_key = os.getenv('AZURE_AI_SEARCH_API_KEY')
            index_name = "agent_workflow_memory"
            if self.use_azure_search and endpoint and api_key:
                from azure.core.credentials import AzureKeyCredential
                credential = AzureKeyCredential(api_key)
                index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
                try:
                    await index_client.get_index(index_name)
                    print(f"✅ Azure AI Search index '{index_name}' exists")
                except ResourceNotFoundError:
                    print(f"⚠️ Index '{index_name}' not found, creating...")
                    # Use the correct 2025 API structure for vector search
                    from azure.search.documents.indexes.models import (
                        SearchField, 
                        SearchFieldDataType,
                        VectorSearchProfile,
                        HnswAlgorithmConfiguration,
                        VectorSearchAlgorithmKind,
                        VectorSearchAlgorithmMetric
                    )
                    
                    # Define fields using SearchField
                    fields = [
                        SearchField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
                        SearchField(name="agent_name", type=SearchFieldDataType.String, filterable=True, searchable=True),
                        SearchField(name="request", type=SearchFieldDataType.String, searchable=True),
                        SearchField(name="response", type=SearchFieldDataType.String, searchable=True),
                        SearchField(name="context", type=SearchFieldDataType.String, searchable=True),
                        SearchField(name="timestamp", type=SearchFieldDataType.String, filterable=True, sortable=True),
                        SearchField(
                            name="embedding",
                            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                            searchable=True,
                            vector_search_dimensions=1536,
                            vector_search_profile_name="vector-profile-1"
                        )
                    ]
                    
                    # Define vector search configuration with algorithms and profiles
                    vector_search = VectorSearch(
                        algorithms=[
                            HnswAlgorithmConfiguration(
                                name="hnsw-algorithm-1",
                                kind=VectorSearchAlgorithmKind.HNSW,
                                parameters={
                                    "metric": VectorSearchAlgorithmMetric.COSINE,
                                    "m": 4,
                                    "efConstruction": 400,
                                    "efSearch": 500
                                }
                            )
                        ],
                        profiles=[
                            VectorSearchProfile(
                                name="vector-profile-1",
                                algorithm_configuration_name="hnsw-algorithm-1"
                            )
                        ]
                    )
                    
                    # Create index with proper configuration
                    index = SearchIndex(
                        name=index_name,
                        fields=fields,
                        vector_search=vector_search
                    )
                    await index_client.create_index(index)
                    print(f"✅ Created Azure AI Search index '{index_name}'")
                finally:
                    await index_client.close()
            else:
                print("✅ Azure AI Search collection ready (in-memory or already exists)")
        except Exception as e:
            print(f"⚠️ Could not verify/create Azure AI Search index: {e}")
    
    @_tracer.start_as_current_span("memory.save")
    async def _save_to_memory(self, agent_name: str, request: str, response: str, context: Dict = None):
        """Save interaction to vector memory with embeddings"""

        if not self.memory_collection:
            return

        import uuid
        from datetime import datetime

        # Get embedding service from kernel
        embedding_service = self.kernel.get_service("text-embedding")
        if embedding_service is None:
            print("❌ Embedding service not found in kernel")
            return

        # Generate embedding for the response
        embedding_input = f"{request} {response}"
        embedding_result = await embedding_service.generate_embeddings([embedding_input])
        embedding_vector = embedding_result[0] if embedding_result is not None and len(embedding_result) > 0 else None
        
        # Create memory record as dict (compatible with both storage types)
        record = {
            "id": str(uuid.uuid4()),
            "agent_name": agent_name,
            "request": request,
            "response": response,
            "context": str(context) if context else "",
            "timestamp": datetime.now().isoformat(),
            "embedding": embedding_vector.tolist() if embedding_vector is not None else None
        }
        
        # Save to collection
        await self.memory_collection.upsert(record)
        print(f"💾 Saved to memory: {agent_name} interaction")
    
    @_tracer.start_as_current_span("memory.search")
    async def _search_memory(self, query: str, top_k: int = 3, filters: Optional[Dict] = None) -> List[Dict]:
        """Search vector memory for relevant past interactions with optional filtering"""

        if not self.memory_collection:
            return []

        # Get embedding service from kernel
        embedding_service = self.kernel.get_service("text-embedding")
        if embedding_service is None:
            print("❌ Embedding service not found in kernel")
            return []

        # Generate embedding for query
        embedding_result = await embedding_service.generate_embeddings([query])
        query_embedding = embedding_result[0] if embedding_result is not None and len(embedding_result) > 0 else None
        
        if query_embedding is None:
            return []
        
        query_embedding_list = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding

        try:
            if hasattr(self.memory_collection, 'vector_search'):
                from semantic_kernel.data import VectorSearchOptions
                search_options = VectorSearchOptions(
                    vector_field_name="embedding",
                    include_vectors=False,
                    top=top_k
                )
                if filters and self.use_azure_search:
                    filter_conditions = []
                    for key, value in filters.items():
                        filter_conditions.append(f"{key} eq '{value}'")
                    if filter_conditions:
                        search_options.filter = " and ".join(filter_conditions)
                results = await self.memory_collection.vector_search(
                    vector=query_embedding_list,
                    options=search_options
                )
            else:
                # In-memory fallback, do not pass with_embeddings
                results = await self.memory_collection.search(
                    vector=query_embedding_list,
                    top=top_k
                )
            records = []
            async for result in results.results:
                if hasattr(result, 'record'):
                    records.append(result.record)
                else:
                    records.append(result)
            return records
        except Exception as e:
            print(f"⚠️ Error during memory search: {e}")
            return []
    
    @_tracer.start_as_current_span("agents.register")
    async def register_agent(self, name: str, agent_type: str, capabilities: List[str]):
        """Register an Azure AI Foundry agent with the orchestrator"""
        
        try:
            # Check if agent already exists
            existing_agents = self.ai_client.agents.list_agents()
            agent = None
            for existing_agent in existing_agents:
                if existing_agent.name == name:
                    agent = existing_agent
                    print(f"♻️  Reusing existing agent: {name}")
                    break
            
            if not agent:
                # Create new agent based on type
                if agent_type == "document_analyst":
                    agent = self.ai_client.agents.create_agent(
                        model=os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
                        name=name,
                        instructions=f"""You are a document analysis expert. Your capabilities include:
                        {', '.join(capabilities)}
                        Analyze documents thoroughly and provide detailed insights."""
                    )
                    
                elif agent_type == "code_executor":
                    agent = self.ai_client.agents.create_agent(
                        model=os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
                        name=name,
                        instructions=f"""You are a code execution and data analysis expert. Your capabilities include:
                        {', '.join(capabilities)}
                        Process data and generate analytical outputs.""",
                        tools=[{"type": "code_interpreter"}]
                    )
                    
                elif agent_type == "function_caller":
                    agent = self.ai_client.agents.create_agent(
                        model=os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
                        name=name,
                        instructions=f"""You are a system integration specialist. Your capabilities include:
                        {', '.join(capabilities)}
                        Integrate with external systems and APIs efficiently."""
                    )
                
                else:
                    raise ValueError(f"Unknown agent type: {agent_type}")
                
                print(f"✅ Created new agent: {name}")
            
            self.agents[name] = agent
            self.agent_capabilities[name] = capabilities
            
            print(f"✅ Registered agent '{name}' with capabilities: {capabilities}")
            return agent
            
        except Exception as e:
            print(f"❌ Failed to register agent {name}: {e}")
            raise
    
    @_tracer.start_as_current_span("agents.route_request")
    async def route_request(self, request: str, context: Optional[Dict] = None) -> str:
        """Intelligently route requests to appropriate agents with memory context"""
        
        # Search memory for relevant past interactions
        memory_results = await self._search_memory(request)
        memory_context = ""
        if memory_results:
            memory_context = "\n\nRelevant past interactions:\n"
            for mem in memory_results:
                # Use attribute access for WorkflowMemoryRecord
                memory_context += f"- Agent {mem.agent_name}: {mem.request[:100]}... → {mem.response[:100]}...\n"
        
        # Use Semantic Kernel to analyze the request and determine routing
        routing_prompt = f"""
        Analyze this request and determine which agent capabilities are needed:
        Request: {request}
        
        {memory_context}
        
        Available agents and their capabilities:
        {self._format_agent_capabilities()}
        
        Return the best agent name to handle this request, or multiple agents if collaboration is needed.
        Format: agent_name or agent1,agent2 for collaboration
        """

        # Use AzureChatPromptExecutionSettings for execution_settings
        from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

        execution_settings = AzureChatPromptExecutionSettings(
            service_id="chat-gpt",
            ai_model_id=os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
            max_tokens=100,
            temperature=0.1
        )

        routing_function = KernelFunction.from_prompt(
            prompt=routing_prompt,
            prompt_template_config=PromptTemplateConfig(
                template=routing_prompt,
                execution_settings=execution_settings
            ),
            function_name="routing_function",
            plugin_name="orchestrator_plugin"
        )
        
        routing_result = await self.kernel.invoke(routing_function)
        selected_agents = str(routing_result).strip().split(',')
        
        # Execute request with selected agent(s)
        if len(selected_agents) == 1:
            return await self._execute_single_agent(selected_agents[0], request, context)
        else:
            return await self._execute_collaborative_workflow(selected_agents, request, context)
    
    @_tracer.start_as_current_span("agents.execute_single")
    async def _execute_single_agent(self, agent_name: str, request: str, context: Optional[Dict]) -> str:
        """Execute request with a single agent and save to memory"""
        
        if agent_name not in self.agents:
            return f"Agent '{agent_name}' not found"
        
        agent = self.agents[agent_name]
        
        # Search for relevant memory context
        memory_results = await self._search_memory(request)
        memory_enhanced_context = context or {}
        if memory_results:
            memory_enhanced_context['relevant_history'] = [
                {
                    'agent': mem.agent_name,
                    'request': mem.request,
                    'response': mem.response[:200]
                }
                for mem in memory_results[:2]  # Top 2 most relevant
            ]
        
        # Add context to request if provided
        if memory_enhanced_context:
            enhanced_request = f"Context: {memory_enhanced_context}\n\nRequest: {request}"
        else:
            enhanced_request = request
        
        try:
            # Create thread and run conversation
            thread = self.ai_client.agents.threads.create()
            self.ai_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=enhanced_request
            )
            
            run = self.ai_client.agents.runs.create(
                thread_id=thread.id,
                agent_id=agent.id
            )
            
            # Wait for completion
            import time
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = self.ai_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
            
            if run.status == "completed":
                messages = self.ai_client.agents.messages.list(thread_id=thread.id)
                for msg in messages:
                    if msg.role == "assistant":
                        response = self._extract_message_content(msg)
                        
                        # Save to memory
                        await self._save_to_memory(agent_name, request, response, memory_enhanced_context)
                        
                        return response
            
            return f"Error: Run ended with status {run.status}"
            
        except Exception as e:
            return f"Error executing agent {agent_name}: {str(e)}"
    
    def _extract_message_content(self, msg) -> str:
        """Extract content from Azure AI message object"""
        if hasattr(msg, 'content') and msg.content:
            if isinstance(msg.content, list) and len(msg.content) > 0:
                content_item = msg.content[0]
                if hasattr(content_item, 'text'):
                    if hasattr(content_item.text, 'value'):
                        return content_item.text.value
                    return str(content_item.text)
                return str(content_item)
            return str(msg.content)
        return ""
    
    @_tracer.start_as_current_span("agents.execute_collaborative")
    async def _execute_collaborative_workflow(self, agent_names: List[str], request: str, context: Optional[Dict]) -> str:
        """Execute collaborative workflow with multiple agents using memory context"""
        
        workflow_results = []
        accumulated_context = context or {}
        
        # Add memory context from the start
        memory_results = await self._search_memory(request)
        if memory_results:
            accumulated_context['workflow_memory'] = [
                {
                    'agent': mem.agent_name,
                    'request': mem.request,
                    'response': mem.response
                }
                for mem in memory_results
            ]
        
        for i, agent_name in enumerate(agent_names):
            # For subsequent agents, include previous results as context
            if i > 0:
                accumulated_context['previous_results'] = workflow_results
            
            result = await self._execute_single_agent(agent_name, request, accumulated_context)
            workflow_results.append({
                'agent': agent_name,
                'result': result
            })
            
            # Update context for next agent
            accumulated_context[f'{agent_name}_output'] = result
        
        # Synthesize final result using Semantic Kernel with memory context
        synthesis_prompt = f"""
        Synthesize the following agent outputs into a comprehensive response:
        Original Request: {request}
        
        Agent Outputs:
        {self._format_workflow_results(workflow_results)}
        
        Relevant Memory Context:
        {[
            {
                'agent_name': mem.agent_name,
                'request': mem.request,
                'response': mem.response
            } for mem in memory_results[:2]
        ] if memory_results else 'No relevant history found'}
        
        Provide a unified, coherent response that combines the insights from all agents.
        """

        # Fix: Use AzureChatPromptExecutionSettings for execution_settings
        from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

        execution_settings = AzureChatPromptExecutionSettings(
            service_id="chat-gpt",
            ai_model_id=os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
            max_tokens=500,
            temperature=0.3
        )

        synthesis_function = KernelFunction.from_prompt(
            prompt=synthesis_prompt,
            prompt_template_config=PromptTemplateConfig(
                template=synthesis_prompt,
                execution_settings=execution_settings
            ),
            function_name="synthesis_function",
            plugin_name="orchestrator_plugin"
        )
        
        final_result = await self.kernel.invoke(synthesis_function)
        
        # Save collaborative result to memory
        await self._save_to_memory(
            agent_name="collaborative_workflow",
            request=request,
            response=str(final_result),
            context={'agents': agent_names, 'workflow_results': workflow_results}
        )
        
        return str(final_result)
    
    def _format_agent_capabilities(self) -> str:
        """Format agent capabilities for routing decisions"""
        formatted = []
        for name, capabilities in self.agent_capabilities.items():
            formatted.append(f"- {name}: {', '.join(capabilities)}")
        return '\n'.join(formatted)
    
    def _format_workflow_results(self, results: List[Dict]) -> str:
        """Format workflow results for synthesis"""
        formatted = []
        for result in results:
            formatted.append(f"Agent {result['agent']}: {result['result'][:200]}...")
        return '\n\n'.join(formatted)
    
    async def demonstrate_memory_aware_workflow(self):
        """Demonstrate how memory enhances agent interactions over time"""
        
        print("\n🧠 Memory-Aware Agent Workflow Demonstration")
        print("=" * 50)
        
        # Show which storage backend is being used
        storage_type = "Azure AI Search" if self.use_azure_search else "In-Memory"
        print(f"📊 Using {storage_type} for vector storage")
        
        # First interaction - no memory yet
        print("\n1️⃣ First interaction (no memory):")
        result1 = await self.route_request("Analyze the impact of AI on healthcare diagnostics")
        print(f"Result: {result1[:200]}...")
        
        # Second interaction - should use memory from first
        print("\n2️⃣ Second interaction (with memory context):")
        result2 = await self.route_request("What are the risks we discussed about AI in healthcare?")
        print(f"Result: {result2[:200]}...")
        
        # Show memory search results with filtering (if using Azure AI Search)
        print("\n📚 Memory search results:")
        
        # Example of filtered search for production scenarios
        filters = {"agent_name": "policy_expert"} if self.use_azure_search else None
        memory_results = await self._search_memory("AI healthcare risks", filters=filters)
        
        for i, mem in enumerate(memory_results[:3]):
            print(f"{i+1}. Agent: {mem.agent_name}, Request: {mem.request[:50]}...")
        
        # Demonstrate hybrid search if using Azure AI Search
        if self.use_azure_search:
            print("\n🔍 Demonstrating hybrid search capabilities...")
            # Azure AI Search supports both vector and keyword search
            hybrid_results = await self._search_memory(
                "healthcare compliance regulations",
                top_k=5
            )
            print(f"Found {len(hybrid_results)} relevant memories using hybrid search")
        
        return {"first_interaction": result1, "second_interaction": result2, "memory_results": memory_results}
    
    async def create_business_workflow(self):
        """Create a complete business workflow demonstration with memory"""
        
        print("🎭 Creating Multi-Agent Business Workflow with Memory")
        
        # Register specialized agents
        await self.register_agent(
            "policy_expert", 
            "document_analyst", 
            ["policy_analysis", "document_search", "compliance_review"]
        )
        
        await self.register_agent(
            "financial_analyst", 
            "code_executor", 
            ["financial_analysis", "data_processing", "report_generation"]
        )
        
        await self.register_agent(
            "integration_specialist", 
            "function_caller", 
            ["system_integration", "data_retrieval", "external_apis"]
        )
        
        # Define business scenarios
        scenarios = [
            {
                "name": "Policy Compliance Review",
                "request": "Review our remote work policy for compliance with new labor regulations and provide recommendations",
                "expected_agents": ["policy_expert"]
            },
            {
                "name": "Financial Performance Analysis", 
                "request": "Analyze Q3 financial data and create performance metrics dashboard",
                "expected_agents": ["financial_analyst"]
            },
            {
                "name": "Integrated Business Report",
                "request": "Create a comprehensive business report combining policy compliance, financial performance, and system integration status",
                "expected_agents": ["policy_expert", "financial_analyst", "integration_specialist"]
            }
        ]
        
        # Execute scenarios
        results = {}
        for scenario in scenarios:
            print(f"\n📋 Executing: {scenario['name']}")
            print("-" * 50)
            
            result = await self.route_request(scenario['request'])
            results[scenario['name']] = result
            
            print(f"Result: {result[:200]}...")
        
        # Demonstrate memory-aware follow-up
        print("\n🔄 Memory-aware follow-up query:")
        follow_up = await self.route_request("Summarize the key findings from our policy and financial reviews")
        results['memory_aware_followup'] = follow_up
        print(f"Follow-up result: {follow_up[:200]}...")
        
        return results

@_tracer.start_as_current_span("demo.sem_kernel_orchestration")
async def demonstrate_semantic_kernel_orchestration():
    """Main demonstration of Semantic Kernel orchestration with memory"""

    try:
        # Load environment variables
        load_dotenv()
        endpoint = os.getenv('AZURE_AI_SEARCH_ENDPOINT')
        api_key = os.getenv('AZURE_AI_SEARCH_API_KEY')

        # Fix: Only use Azure AI Search if BOTH endpoint and api_key are set and non-empty
        use_azure_search = bool(endpoint and api_key)

        print("DEBUG: AZURE_AI_SEARCH_ENDPOINT =", endpoint)
        print("DEBUG: AZURE_AI_SEARCH_API_KEY =", api_key)

        if use_azure_search:
            print("🚀 Using Azure AI Search for production-grade vector storage")
        else:
            print("💡 Azure AI Search not configured, using in-memory storage")
            print("   Set AZURE_AI_SEARCH_ENDPOINT and AZURE_AI_SEARCH_API_KEY for production")

        orchestrator = MultiAgentOrchestrator(use_azure_search=use_azure_search)
        # Run business workflow
        workflow_results = await orchestrator.create_business_workflow()
        
        # Demonstrate memory capabilities
        memory_demo = await orchestrator.demonstrate_memory_aware_workflow()
        
        # Convert WorkflowMemoryRecord objects to dicts for JSON serialization
        from dataclasses import asdict
        if "memory_demonstration" in workflow_results:
            demo = workflow_results["memory_demonstration"]
            # Convert memory_results if present and is a list
            if "memory_results" in demo and isinstance(demo["memory_results"], list):
                demo["memory_results"] = [asdict(mem) for mem in demo["memory_results"]]
            workflow_results["memory_demonstration"] = demo
        
        print("\n🎉 Advanced Multi-Agent Orchestration Complete!")
        
        # Save results
        from pathlib import Path
        import json
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        with open(output_dir / "advanced_orchestration_results.json", "w") as f:
            json.dump(workflow_results, f, indent=2)
        
        print(f"📄 Results saved to {output_dir}/advanced_orchestration_results.json")
        
        # Ensure spans are exported before process exits
        try:
            provider = trace.get_tracer_provider()
            if hasattr(provider, "force_flush"):
                provider.force_flush()
        except Exception:
            pass

        return workflow_results

    except Exception as e:
        print(f"❌ Error in orchestration: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(demonstrate_semantic_kernel_orchestration())
