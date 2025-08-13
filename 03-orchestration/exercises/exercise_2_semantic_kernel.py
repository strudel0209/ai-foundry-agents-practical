#!/usr/bin/env python3

import os
import asyncio
import json
from typing import Dict, Any, Optional, List, AsyncIterable
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import enable_telemetry

# Load environment variables
load_dotenv()

# Set consistent service name for filtering and enable content capture
os.environ.setdefault("OTEL_SERVICE_NAME", "semantic-kernel-agents")
os.environ.setdefault("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")

enable_telemetry()

# Semantic Kernel imports
import semantic_kernel as sk
from semantic_kernel.agents import Agent
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from semantic_kernel.kernel import Kernel

# Azure AI Foundry imports
from azure.ai.projects import AIProjectClient

# OpenTelemetry / Azure Monitor
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.trace.status import Status, StatusCode
from azure.monitor.opentelemetry import configure_azure_monitor

# === TRACING SETUP ===

def configure_tracing(project_endpoint: Optional[str]) -> None:
    """
    Configure Azure Monitor OpenTelemetry exporters.
    Prefers the project's Application Insights connection string; falls back to env var.
    """
    env_conn = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    connection_string = env_conn

    if not connection_string and project_endpoint:
        try:
            tmp_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=DefaultAzureCredential()
            )
            connection_string = tmp_client.telemetry.get_application_insights_connection_string()
            if connection_string:
                print("✅ Using Application Insights connection string from Azure AI Foundry project")
        except Exception as e:
            print(f"⚠️ Could not get connection string from project: {e}")

    if connection_string:
        configure_azure_monitor(
            connection_string=connection_string,
            service_name=os.getenv("OTEL_SERVICE_NAME", "semantic-kernel-agents"),
            service_version="1.0.0",
        )
        # Optional: include trace/span ids in logs
        LoggingInstrumentor().instrument(set_logging_format=True)
        print("✅ Azure Monitor OpenTelemetry configured")
    else:
        print("⚠️ No Application Insights connection string found; traces won’t be sent to Azure Monitor.")

# Get a tracer for custom spans
tracer = trace.get_tracer(__name__)

# --- Direct SK Agent wrapper for Azure AI Foundry agents ---

class AzureAIFoundrySKAgent(Agent):
    """
    Semantic Kernel Agent that wraps an Azure AI Foundry agent.
    """
    def __init__(self, project_client: AIProjectClient, foundry_agent, name: str, description: str = "", kernel: Optional[Kernel] = None):
        if kernel is None:
            kernel = Kernel()

        super().__init__(
            service_id=name,
            kernel=kernel,
            name=name,
            description=description
        )
        self._project_client = project_client
        self._foundry_agent = foundry_agent

    async def invoke(self, messages: List[ChatMessageContent]) -> AsyncIterable[ChatMessageContent]:
        """
        Implements the SK Agent interface.
        """
        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.role == AuthorRole.USER:
                user_message = str(msg.content)
                break

        if not user_message:
            user_message = str(messages[-1].content) if messages else ""

        response = await self.get_response(user_message)
        yield ChatMessageContent(role=AuthorRole.ASSISTANT, content=response, name=self.name)

    async def invoke_stream(self, messages: List[ChatMessageContent]) -> AsyncIterable[ChatMessageContent]:
        """
        Streaming (falls back to non-streaming).
        """
        async for message in self.invoke(messages):
            yield message

    @tracer.start_as_current_span("agent_response")
    async def get_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get response from Azure AI Foundry agent with proper tracing.
        """
        span = trace.get_current_span()
        span.set_attribute("agent.name", self.name)
        span.set_attribute("agent.id", self._foundry_agent.id)
        span.set_attribute("input.message", (message or "")[:500])  # Truncate for readability

        try:
            # Create thread - automatically traced by Azure SDK
            thread = self._project_client.agents.threads.create()
            span.set_attribute("thread.id", thread.id)

            # Create message
            self._project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )

            # Create run and wait for completion
            run = self._project_client.agents.runs.create(
                thread_id=thread.id,
                agent_id=self._foundry_agent.id
            )
            span.set_attribute("run.id", run.id)

            # Async-friendly polling loop
            max_wait_time = 60  # seconds
            loop = asyncio.get_running_loop()
            start_time = loop.time()

            while run.status in ("queued", "in_progress", "requires_action"):
                if loop.time() - start_time > max_wait_time:
                    span.set_attribute("timeout", True)
                    span.set_attribute("run.status", "timeout")
                    return f"Error: Request timed out after {max_wait_time} seconds"

                await asyncio.sleep(1)
                run = self._project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)

                if run.status == "requires_action":
                    # Record tool-calling requirement if added later
                    span.add_event("run.requires_action", {"run.id": run.id})
                    break

            span.set_attribute("run.status", run.status)

            if run.status == "completed":
                messages = self._project_client.agents.messages.list(thread_id=thread.id)
                for msg in messages:
                    if getattr(msg, "role", None) == "assistant":
                        result = ""
                        if hasattr(msg, "content") and msg.content:
                            if isinstance(msg.content, list) and len(msg.content) > 0:
                                content_item = msg.content[0]
                                if hasattr(content_item, "text"):
                                    result = getattr(content_item.text, "value", str(content_item.text))
                                else:
                                    result = str(content_item)
                            else:
                                result = str(msg.content)

                        span.set_attribute("output.message", (result or "")[:500])
                        return result

            return f"Error: Run ended with status {run.status}"

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            return f"Error: {str(e)}"

# --- Orchestrator ---

class SemanticKernelOrchestrator:
    """
    Semantic Kernel orchestration with Azure AI Foundry.
    """

    def __init__(self):
        self.kernel = None
        self.foundry_agents = {}
        self.sk_agents = {}
        self.ai_client = None
        self.credential = DefaultAzureCredential()

    async def setup_kernel(self):
        """Initialize Semantic Kernel with AI Project client for tracing"""
        print("🧠 Setting up Semantic Kernel...")
        self.kernel = Kernel()

        project_endpoint = os.getenv('PROJECT_ENDPOINT')
        if not project_endpoint:
            raise ValueError("PROJECT_ENDPOINT environment variable is not set")

        # Configure tracing before client usage to ensure consistent parent/child spans
        configure_tracing(project_endpoint)

        # Initialize AI client
        self.ai_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=self.credential
        )

        print("✅ Semantic Kernel initialized")

    async def create_azure_ai_foundry_agents(self):
        """Create or reuse Azure AI Foundry agents"""
        print("🤖 Creating Azure AI Foundry agents...")

        agent_configs = [
            {
                'name': 'research-specialist',
                'model': os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
                'instructions': """You are a research specialist. Your role:
                - Gather comprehensive information on topics
                - Identify credible sources and data
                - Synthesize findings into clear summaries
                - Highlight key insights and trends"""
            },
            {
                'name': 'analysis-specialist',
                'model': os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
                'instructions': """You are an analysis expert. Your role:
                - Analyze research data for patterns
                - Identify strategic opportunities
                - Assess risks and challenges
                - Provide data-driven recommendations"""
            },
            {
                'name': 'writing-specialist',
                'model': os.getenv('MODEL_DEPLOYMENT_NAME', 'gpt-4o-mini'),
                'instructions': """You are a professional writer. Your role:
                - Transform analysis into polished documents
                - Maintain professional tone and style
                - Structure content with clear sections
                - Create executive summaries"""
            }
        ]

        for config in agent_configs:
            try:
                # Check if agent exists
                existing = self.ai_client.agents.list_agents()
                agent = None
                for existing_agent in existing:
                    if existing_agent.name == config['name']:
                        agent = existing_agent
                        break

                if not agent:
                    agent = self.ai_client.agents.create_agent(
                        model=config['model'],
                        name=config['name'],
                        instructions=config['instructions']
                    )
                    print(f"✅ Created agent: {config['name']}")
                else:
                    print(f"♻️  Reusing agent: {config['name']}")

                self.foundry_agents[config['name']] = agent
                self.sk_agents[config['name']] = AzureAIFoundrySKAgent(
                    project_client=self.ai_client,
                    foundry_agent=agent,
                    name=config['name'],
                    description=config['instructions'].split('\n')[0],
                    kernel=self.kernel
                )

            except Exception as e:
                print(f"❌ Failed with {config['name']}: {e}")

        print(f"📊 Azure AI Foundry SK agents ready: {len(self.sk_agents)}")

    @tracer.start_as_current_span("sequential_orchestration")
    async def demonstrate_sequential_orchestration(self, topic: str, focus_area: str = ""):
        """Sequential orchestration"""
        span = trace.get_current_span()
        span.set_attribute("orchestration.type", "sequential")
        span.set_attribute("topic", topic)

        print("\n🔄 Sequential Multi-Agent Orchestration")
        print("=" * 60)

        initial_message = f"""
        Create a comprehensive report on: {topic}
        Focus area: {focus_area if focus_area else 'General overview'}
        Please coordinate the following:
        1. Research the topic thoroughly
        2. Analyze the findings for insights
        3. Create a professional document with recommendations
        """

        print(f"📋 Task: {topic}")
        print("🚀 Starting sequential orchestration...\n")

        results = []
        current_message = initial_message

        agents_sequence = [
            ('research-specialist', 'Research Phase'),
            ('analysis-specialist', 'Analysis Phase'),
            ('writing-specialist', 'Writing Phase')
        ]

        for agent_name, phase in agents_sequence:
            print(f"\n📌 {phase}: {agent_name}")
            agent = self.sk_agents[agent_name]

            messages = [ChatMessageContent(role=AuthorRole.USER, content=current_message)]

            async for response in agent.invoke(messages):
                print(f"💬 {agent.name}: {response.content[:200]}...")
                results.append({
                    "agent": agent.name,
                    "phase": phase,
                    "content": response.content,
                    "timestamp": datetime.now().isoformat()
                })
                current_message = f"Based on the previous work: {response.content}\n\nPlease continue with your specialized task."

        return results

    @tracer.start_as_current_span("roundrobin_orchestration")
    async def demonstrate_roundrobin_orchestration(self, topic: str):
        """Round-robin orchestration"""
        span = trace.get_current_span()
        span.set_attribute("orchestration.type", "roundrobin")
        span.set_attribute("topic", topic)

        print("\n🔁 Round-Robin Multi-Agent Discussion")
        print("=" * 60)
        print(f"💭 Discussion topic: {topic}")
        print("🔄 Starting round-robin discussion...\n")

        discussion = []
        messages_history = [ChatMessageContent(role=AuthorRole.USER, content=f"Let's discuss: {topic}")]

        num_rounds = 2  # Reduced for faster demo

        for round_num in range(num_rounds):
            print(f"\n--- Round {round_num + 1} ---")
            for agent_name in self.sk_agents.keys():
                agent = self.sk_agents[agent_name]

                async for response in agent.invoke(messages_history):
                    print(f"💬 {agent.name}: {response.content[:150]}...")
                    discussion.append({
                        "round": round_num + 1,
                        "agent": agent.name,
                        "content": response.content,
                        "timestamp": datetime.now().isoformat()
                    })
                    messages_history.append(response)

        return discussion

    @tracer.start_as_current_span("hybrid_orchestration")
    async def demonstrate_hybrid_orchestration(self, goal: str):
        """Hybrid orchestration"""
        span = trace.get_current_span()
        span.set_attribute("orchestration.type", "hybrid")
        span.set_attribute("goal", goal)

        print("\n🔀 Hybrid Orchestration")
        print("=" * 60)
        results = {}

        # Phase 1: Research
        print("\n📌 Phase 1: Research Specialist")
        research_result = await self.sk_agents['research-specialist'].get_response(
            f"Research this topic: {goal}"
        )
        results['research'] = research_result
        print(f"Research: {research_result[:200]}...")

        # Phase 2: Analysis
        print("\n📌 Phase 2: Analysis Specialist")
        analysis_result = await self.sk_agents['analysis-specialist'].get_response(
            f"Analyze these findings: {research_result}"
        )
        results['analysis'] = analysis_result
        print(f"Analysis: {analysis_result[:200]}...")

        # Phase 3: Writing
        print("\n📌 Phase 3: Writing Specialist")
        writing_result = await self.sk_agents['writing-specialist'].get_response(
            f"Create executive briefing from: {analysis_result}"
        )
        results['final_document'] = writing_result
        print(f"Document: {writing_result[:200]}...")

        return results

    @tracer.start_as_current_span("main_orchestration")
    async def demonstrate_orchestration(self):
        """Main demonstration"""
        print("🌟 Semantic Kernel Agent Orchestration with Azure AI Foundry")
        print("=" * 70)

        await self.setup_kernel()
        await self.create_azure_ai_foundry_agents()

        if not self.sk_agents:
            print("\n❌ No agents were created successfully.")
            return {}

        results = {}

        # Demo 1: Sequential
        sequential_results = await self.demonstrate_sequential_orchestration(
            topic="AI in Healthcare",
            focus_area="Diagnostic imaging"
        )
        results['sequential'] = sequential_results

        # Demo 2: Round-robin
        roundrobin_results = await self.demonstrate_roundrobin_orchestration(
            topic="Quantum Computing impact"
        )
        results['roundrobin'] = roundrobin_results

        # Demo 3: Hybrid
        hybrid_results = await self.demonstrate_hybrid_orchestration(
            goal="Sustainable energy future"
        )
        results['hybrid'] = hybrid_results

        # Summary
        print("\n\n📊 ORCHESTRATION SUMMARY")
        print("=" * 60)
        print(f"✅ Sequential: {len(results.get('sequential', []))} interactions")
        print(f"✅ Round-robin: {len(results.get('roundrobin', []))} turns")
        print(f"✅ Hybrid: {len(results.get('hybrid', {}))} phases")

        return results

async def main():
    """Main execution"""
    orchestrator = SemanticKernelOrchestrator()

    try:
        results = await orchestrator.demonstrate_orchestration()

        print("\n\n✅ All demonstrations completed!")
        print("\n🔍 TRACING INFORMATION:")
        print(f"   - Connection String (env): {os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING', 'Not set')[:50]}...")
        print("   - View traces in Azure AI Foundry portal > Your Project > Observability > Tracing")
        print("   - Or in Application Insights > Transaction Search")
        print(f"   - Service name: {os.getenv('OTEL_SERVICE_NAME', 'semantic-kernel-agents')}")

        # Save results
        from pathlib import Path
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "sk_orchestration.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📁 Results saved to {output_dir}/sk_orchestration.json")

        return results

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    print("🚀 Starting Semantic Kernel Agent Orchestration")
    print("-" * 70)
    asyncio.run(main())
