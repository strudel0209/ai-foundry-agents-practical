#!/usr/bin/env python3

import os
import asyncio
import json
from typing import Dict, Any, Optional, List, AsyncIterable
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

# Semantic Kernel imports
import semantic_kernel as sk
from semantic_kernel.agents import Agent
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from semantic_kernel.kernel import Kernel

# Azure AI Foundry imports
from azure.ai.projects import AIProjectClient

# --- NEW: Direct SK Agent wrapper for Azure AI Foundry agents ---

class AzureAIFoundrySKAgent(Agent):
    """
    Semantic Kernel Agent that wraps an Azure AI Foundry agent.
    Implements the SK Agent interface for direct orchestration.
    """
    def __init__(self, project_client: AIProjectClient, foundry_agent, name: str, description: str = "", kernel: Optional[Kernel] = None):
        # Initialize the base Agent class with required kernel
        if kernel is None:
            kernel = Kernel()  # Create a minimal kernel if not provided
        
        super().__init__(
            service_id=name,
            kernel=kernel,  # Provide the kernel instance
            name=name,
            description=description
        )
        # Use different attribute names to avoid Pydantic validation conflicts
        self._project_client = project_client
        self._foundry_agent = foundry_agent

    async def invoke(self, messages: List[ChatMessageContent]) -> AsyncIterable[ChatMessageContent]:
        """
        Implements the SK Agent interface for invoking the agent.
        """
        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.role == AuthorRole.USER:
                user_message = str(msg.content)
                break
        
        if not user_message:
            # If no user message, use the last message
            user_message = str(messages[-1].content) if messages else ""
        
        response = await self.get_response(user_message)
        yield ChatMessageContent(role=AuthorRole.ASSISTANT, content=response, name=self.name)

    async def invoke_stream(self, messages: List[ChatMessageContent]) -> AsyncIterable[ChatMessageContent]:
        """
        Implements the SK Agent interface for streaming responses.
        Since Azure AI Foundry agents don't support streaming, we'll yield the full response at once.
        """
        async for message in self.invoke(messages):
            yield message

    async def get_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handles a single-turn message and returns the response from the Azure AI Foundry agent.
        """
        try:
            # Use the correct API: threads.create() instead of create_thread()
            thread = self._project_client.agents.threads.create()
            self._project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )
            run = self._project_client.agents.runs.create(
                thread_id=thread.id,
                agent_id=self._foundry_agent.id
            )
            import time
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = self._project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
                
                # Handle requires_action status (for function calling)
                if run.status == "requires_action":
                    # For now, we'll skip function calling and let it fail
                    break
                    
            if run.status == "completed":
                # Handle ItemPaged object properly
                messages = self._project_client.agents.messages.list(thread_id=thread.id)
                # Iterate through the ItemPaged object
                for msg in messages:
                    if msg.role == "assistant":
                        # Handle different content types
                        if hasattr(msg, 'content') and msg.content:
                            if isinstance(msg.content, list) and len(msg.content) > 0:
                                # Handle content as a list of content items
                                content_item = msg.content[0]
                                if hasattr(content_item, 'text'):
                                    if hasattr(content_item.text, 'value'):
                                        return content_item.text.value
                                    else:
                                        return str(content_item.text)
                                else:
                                    return str(content_item)
                            else:
                                # Handle content as a direct value
                                return str(msg.content)
            elif run.status == "failed":
                error_msg = getattr(run, 'last_error', 'Unknown error')
                return f"Error: Run failed - {error_msg}"
            elif run.status == "cancelled":
                return "Error: Run was cancelled"
            elif run.status == "expired":
                return "Error: Run expired"
            else:
                return f"Error: Run ended with status {run.status}"
        except Exception as e:
            return f"Error: {str(e)}"

# --- Orchestrator using direct SK agent wrappers ---

class SemanticKernelOrchestrator:
    """
    Modern Semantic Kernel orchestration with direct Azure AI Foundry agent wrappers.
    Demonstrates best practices for agent orchestration (July 2025).
    """

    def __init__(self):
        load_dotenv()
        self.kernel: Optional[Kernel] = None
        self.foundry_agents: Dict[str, Any] = {}  # Azure AI Foundry agent objects
        self.sk_agents: Dict[str, AzureAIFoundrySKAgent] = {}  # SK agent wrappers
        self.ai_client: Optional[AIProjectClient] = None
        self.credential = DefaultAzureCredential()

    async def setup_kernel(self):
        """Initialize Semantic Kernel (no plugin indirection needed)"""
        print("🧠 Setting up Semantic Kernel...")
        self.kernel = Kernel()
        # No need to add Azure OpenAI service unless you want to use SK-native LLM agents
        # This demo focuses on Foundry agent orchestration
        self.ai_client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=self.credential
        )
        print("✅ Semantic Kernel initialized")

    async def create_azure_ai_foundry_agents(self):
        """Create or reuse Azure AI Foundry agents and wrap them as SK agents"""
        print("🤖 Creating Azure AI Foundry agents and SK wrappers...")
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
                # Handle ItemPaged object when listing agents
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
                # Wrap as SK agent with the shared kernel
                self.sk_agents[config['name']] = AzureAIFoundrySKAgent(
                    project_client=self.ai_client,  # Changed parameter name
                    foundry_agent=agent,
                    name=config['name'],
                    description=config['instructions'].split('\n')[0],
                    kernel=self.kernel  # Pass the kernel instance
                )
            except Exception as e:
                print(f"❌ Failed with {config['name']}: {e}")
        print(f"📊 Azure AI Foundry SK agents ready: {len(self.sk_agents)}")

    async def demonstrate_sequential_orchestration(self, topic: str, focus_area: str = ""):
        """
        Demonstrate sequential orchestration: research → analysis → writing.
        Each step is handled by a direct SK agent wrapper for a Foundry agent.
        """
        print("\n🔄 Sequential Multi-Agent Orchestration (Direct SK→Foundry)")
        print("=" * 60)
        
        # Create initial message
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
        
        # Sequential execution
        agents_sequence = [
            ('research-specialist', 'Research Phase'),
            ('analysis-specialist', 'Analysis Phase'),
            ('writing-specialist', 'Writing Phase')
        ]
        
        for agent_name, phase in agents_sequence:
            print(f"\n📌 {phase}: {agent_name}")
            agent = self.sk_agents[agent_name]
            
            # Create chat message
            messages = [ChatMessageContent(role=AuthorRole.USER, content=current_message)]
            
            # Get response from agent
            async for response in agent.invoke(messages):
                print(f"💬 {agent.name}: {response.content[:200]}..." if len(response.content) > 200 else f"💬 {agent.name}: {response.content}")
                results.append({
                    "agent": agent.name,
                    "phase": phase,
                    "content": response.content
                })
                # Use this response as input for next agent
                current_message = f"Based on the previous work: {response.content}\n\nPlease continue with your specialized task."
        
        return results

    async def demonstrate_roundrobin_orchestration(self, topic: str):
        """
        Demonstrate round-robin discussion with Foundry agents.
        Each agent takes turns contributing to the discussion.
        """
        print("\n🔁 Round-Robin Multi-Agent Discussion (Direct SK→Foundry)")
        print("=" * 60)
        
        print(f"💭 Discussion topic: {topic}")
        print("🔄 Starting round-robin discussion...\n")
        
        discussion = []
        messages_history = [ChatMessageContent(role=AuthorRole.USER, content=f"Let's discuss the implications of: {topic}")]
        
        # 5 rounds of discussion
        for round_num in range(5):
            print(f"\n--- Round {round_num + 1} ---")
            for agent_name in ['research-specialist', 'analysis-specialist', 'writing-specialist']:
                agent = self.sk_agents[agent_name]
                
                # Agent responds to the conversation history
                async for response in agent.invoke(messages_history):
                    print(f"💬 {agent.name}: {response.content[:150]}..." if len(response.content) > 150 else f"💬 {agent.name}: {response.content}")
                    discussion.append({
                        "round": round_num + 1,
                        "agent": agent.name,
                        "content": response.content
                    })
                    # Add to conversation history
                    messages_history.append(response)
        
        return discussion

    async def demonstrate_hybrid_orchestration(self, goal: str):
        """
        Demonstrate a hybrid pattern: sequential orchestration with
        direct calls to Foundry agents at each phase.
        """
        print("\n🔀 Hybrid Orchestration (Direct SK→Foundry, multi-phase)")
        print("=" * 60)
        results = {}
        
        # Phase 1: Research
        print("\n📌 Phase 1: Research Specialist")
        research_result = await self.sk_agents['research-specialist'].get_response(
            f"Research this topic comprehensively: {goal}"
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

    async def demonstrate_orchestration(self):
        """
        Main demonstration of all orchestration patterns using direct SK→Foundry agent wrappers.
        """
        print("🌟 Semantic Kernel Agent-Based Orchestration Demo (Direct SK→Foundry)")
        print("Showcasing latest patterns for Azure AI agent coordination")
        print("=" * 70)
        await self.setup_kernel()
        await self.create_azure_ai_foundry_agents()
        
        # Check if any agents were created successfully
        if not self.sk_agents:
            print("\n❌ No agents were created successfully. Please check your configuration.")
            return {}
        
        results = {}
        
        # Demo 1: Sequential orchestration
        print("\n\n📍 DEMO 1: Sequential Multi-Agent Orchestration")
        sequential_results = await self.demonstrate_sequential_orchestration(
            topic="AI in Healthcare",
            focus_area="Diagnostic imaging and predictive analytics"
        )
        results['sequential'] = sequential_results
        
        # Demo 2: Round-robin orchestration
        print("\n\n📍 DEMO 2: Round-Robin Multi-Agent Discussion")
        roundrobin_results = await self.demonstrate_roundrobin_orchestration(
            topic="Quantum Computing impact on Cryptography"
        )
        results['roundrobin'] = roundrobin_results
        
        # Demo 3: Hybrid orchestration
        print("\n\n📍 DEMO 3: Hybrid SK + Azure AI Orchestration")
        hybrid_results = await self.demonstrate_hybrid_orchestration(
            goal="Future of sustainable energy technologies"
        )
        results['hybrid'] = hybrid_results
        
        # Summary
        print("\n\n📊 ORCHESTRATION SUMMARY")
        print("=" * 60)
        print(f"✅ Sequential orchestration: {len(results.get('sequential', []))} agent interactions")
        print(f"✅ Round-robin discussion: {len(results.get('roundrobin', []))} turns")
        print(f"✅ Hybrid orchestration: {len(results.get('hybrid', {}))} phases completed")
        
        return results

async def main():
    """Main execution function"""
    orchestrator = SemanticKernelOrchestrator()
    try:
        results = await orchestrator.demonstrate_orchestration()
        print("\n\n✅ All demonstrations completed successfully!")
        
        # Save results
        from pathlib import Path
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "sk_agent_orchestration_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📁 Results saved to {output_dir}/sk_agent_orchestration_results.json")
        
        return results
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("🚀 Semantic Kernel Agent-Based Orchestration Demo (Direct SK→Foundry)")
    print("-" * 70)
    asyncio.run(main())
