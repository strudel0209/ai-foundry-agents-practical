"""Exercise 2: Creating Your First Azure AI Agent with Agent Framework."""

import asyncio
import json
import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

PROJECT_ENDPOINT_KEYS = ("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_KEYS = ("AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME")
AGENT_ID_KEYS = ("AZURE_AI_AGENT_ID", "AGENT_ID")
AGENT_CACHE_PATH = Path(__file__).with_suffix(".agent_cache.json")

AGENT_INSTRUCTIONS = """
You are a friendly and knowledgeable Azure AI assistant specializing in helping users
learn Microsoft Agent Framework and Azure AI Foundry.

Your personality:
- Enthusiastic about AI and technology
- Patient and encouraging with learners
- Clear and concise in explanations
- Practical and example-focused

Your expertise:
- Azure AI Foundry platform
- Agent development patterns
- Python programming
- Best practices for AI applications

Communication style:
- Use a warm, professional tone
- Break down complex concepts into digestible parts
- Provide specific examples when possible
- Ask clarifying questions when needed
- Always end with actionable next steps

When helping with code or technical topics:
- Explain the "why" behind recommendations
- Point out potential pitfalls
- Suggest improvements and alternatives
- Encourage experimentation and learning
""".strip()


def _require_env(possible_keys: Iterable[str], description: str) -> str:
    for key in possible_keys:
        value = os.getenv(key)
        if value:
            return value
    joined = ", ".join(possible_keys)
    raise EnvironmentError(f"Missing {description}. Set one of: {joined}")


def _determine_agent_identity(agent_name: str) -> Tuple[Optional[str], str]:
    """Return a known agent_id (if any) and describe its source."""

    for key in AGENT_ID_KEYS:
        value = os.getenv(key)
        if value:
            return value.strip(), f"environment variable '{key}'"

    if AGENT_CACHE_PATH.exists():
        try:
            cache = json.loads(AGENT_CACHE_PATH.read_text())
            cached_value = cache.get(agent_name)
            if cached_value:
                return cached_value, f"cache file {AGENT_CACHE_PATH.name}"
        except json.JSONDecodeError:
            console.print(f"⚠️ Could not parse {AGENT_CACHE_PATH}; ignoring cached IDs.")

    return None, "(not cached yet)"


def _persist_agent_identity(agent_name: str, agent_id: str) -> None:
    try:
        data = json.loads(AGENT_CACHE_PATH.read_text()) if AGENT_CACHE_PATH.exists() else {}
    except json.JSONDecodeError:
        data = {}

    data[agent_name] = agent_id
    AGENT_CACHE_PATH.write_text(json.dumps(data, indent=2))
    console.print(f"💾 Cached agent id {agent_id} for '{agent_name}' in {AGENT_CACHE_PATH}.")

async def create_agent() -> tuple[ChatAgent, DefaultAzureCredential, AzureAIAgentClient, str, str, str, str]:
    """Instantiate ChatAgent backed by Azure AI Foundry."""

    console.print(Panel.fit("🤖 Creating Your First Azure AI Agent", style="bold blue"))
    load_dotenv()

    endpoint = _require_env(PROJECT_ENDPOINT_KEYS, "Azure AI project endpoint")
    model_deployment = _require_env(MODEL_DEPLOYMENT_KEYS, "model deployment name")
    agent_name = os.getenv("AZURE_AI_AGENT_NAME", "Learning-Assistant")
    agent_id, agent_id_source = _determine_agent_identity(agent_name)

    console.print("\n🔧 [bold]Initializing Microsoft Agent Framework client...[/bold]")
    credential = DefaultAzureCredential()

    chat_client = AzureAIAgentClient(
        project_endpoint=endpoint,
        model_deployment_name=model_deployment,
        async_credential=credential,
        agent_name=agent_name,
        agent_id=agent_id,
        use_latest_version=True,
        should_cleanup_agent=False,
    )

    console.print(
        "✅ Client configured; "
        + (f"reusing agent from {agent_id_source}" if agent_id else "creating agent if it doesn't exist")
    )
    agent = ChatAgent(chat_client=chat_client, instructions=AGENT_INSTRUCTIONS)
    return agent, credential, chat_client, endpoint, model_deployment, agent_name, agent_id_source

async def demonstrate_agent_properties(agent: ChatAgent, endpoint: str, model_deployment: str, agent_name: str) -> None:
    """Display agent metadata available from Agent Framework."""

    console.print("\n🔍 [bold]Exploring agent properties...[/bold]")

    details_table = Table(title="Agent Details")
    details_table.add_column("Property", style="cyan")
    details_table.add_column("Value", style="white")

    metadata = getattr(agent, "metadata", None)
    agent_id: Optional[str] = getattr(metadata, "agent_id", None)
    model_name: Optional[str] = getattr(metadata, "model", None)

    details_table.add_row("Endpoint", endpoint)
    details_table.add_row("Model Deployment", model_deployment)
    details_table.add_row("Agent Name", agent_name)
    details_table.add_row("Agent ID", agent_id or "(Assigned after first run)")
    details_table.add_row("Model", model_name or "(Using deployment)")
    details_table.add_row(
        "Instructions Preview",
        AGENT_INSTRUCTIONS[:100] + "..." if len(AGENT_INSTRUCTIONS) > 100 else AGENT_INSTRUCTIONS,
    )

    console.print(details_table)


async def test_agent_conversation(agent: ChatAgent) -> List[dict[str, str]]:
    """Send sample questions through ChatAgent to demonstrate conversation flow and capture history."""

    console.print(f"\n💬 [bold]Testing conversation with {getattr(agent, 'name', 'your agent')}...[/bold]")

    test_questions = [
        "Hello! I'm new to Azure AI agents. Can you explain what makes them so powerful for building AI applications?",
        "What are the key components I need to understand when building my first agent?",
        "Can you give me a practical example of when I would use an Azure AI agent versus a regular chatbot?",
    ]

    conversation_history: List[dict[str, str]] = []

    for i, question in enumerate(test_questions, 1):
        console.print(f"\n🔄 [bold]Test Question {i}/{len(test_questions)}[/bold]")
        console.print(f"👤 [bold blue]User:[/bold blue] {question}")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("🤖 Agent is thinking...", total=None)
            response = await agent.run(question)
            progress.update(task, description="✅ Response ready")

        response_text = response.text.strip() if response.text else "(No text response)"
        console.print(f"\n🤖 [bold green]Alex:[/bold green] {response_text}")
        conversation_history.append({"role": "user", "content": question})
        conversation_history.append({"role": "assistant", "content": response_text})

        if i < len(test_questions):
            console.print("\n" + "─" * 50)

    return conversation_history


def display_conversation_history(history: List[dict[str, str]]) -> None:
    """Render a compact summary of the captured conversation turns."""

    console.print("\n🧠 [bold]Conversation Memory[/bold]")
    history_table = Table(show_lines=True)
    history_table.add_column("Turn", style="magenta")
    history_table.add_column("Role", style="cyan")
    history_table.add_column("Content", style="white")

    for idx in range(0, len(history), 2):
        user_turn = history[idx]
        assistant_turn = history[idx + 1] if idx + 1 < len(history) else {"role": "assistant", "content": "(missing response)"}
        turn_number = (idx // 2) + 1
        history_table.add_row(str(turn_number), user_turn["role"].title(), user_turn["content"])
        history_table.add_row("", assistant_turn["role"].title(), assistant_turn["content"])

    console.print(history_table)

async def main() -> None:
    """Create, inspect, and chat with a Microsoft Agent Framework agent."""

    agent: Optional[ChatAgent] = None
    credential: Optional[DefaultAzureCredential] = None
    chat_client: Optional[AzureAIAgentClient] = None
    endpoint: Optional[str] = None
    model_deployment: Optional[str] = None
    agent_name: Optional[str] = None
    agent_id_source: Optional[str] = None
    conversation_history: List[dict[str, str]] = []

    try:
        (
            agent,
            credential,
            chat_client,
            endpoint,
            model_deployment,
            agent_name,
            agent_id_source,
        ) = await create_agent()

        async with agent:
            await demonstrate_agent_properties(agent, endpoint, model_deployment, agent_name)
            conversation_history = await test_agent_conversation(agent)

        display_conversation_history(conversation_history)

        console.print(Panel.fit(
            "🎉 [bold green]Congratulations![/bold green]\n\n"
            "You've successfully:\n"
            "• Built a Microsoft Agent Framework chat agent\n"
            "• Connected it to Azure AI Foundry deployments\n"
            "• Ran multi-turn conversations using agent.run()\n"
            "• Inspected agent configuration details\n\n"
            "🚀 Next: Explore threads, runs, and tooling in the following exercises.",
            style="bold green",
            title="✅ SUCCESS",
        ))

        console.print(Panel(
            "💡 [bold]Key Learnings:[/bold]\n\n"
            "1. [cyan]Authentication[/cyan]: DefaultAzureCredential works seamlessly with Agent Framework\n"
            "2. [cyan]Agent Creation[/cyan]: ChatAgent wraps Azure AI Foundry agents without manual thread management\n"
            "3. [cyan]Conversation Flow[/cyan]: agent.run() keeps context for multi-turn chats\n"
            "4. [cyan]Observability[/cyan]: Metadata exposes agent + model identifiers\n"
            "5. [cyan]Next Steps[/cyan]: Extend this agent with tools in upcoming modules",
            title="📚 Learning Summary",
        ))

    except KeyboardInterrupt:
        console.print("\n👋 Exercise interrupted by user")
    except Exception as exc:
        console.print(f"\n💥 [bold red]Unexpected error:[/bold red] {exc}")
        console.print("\n💡 [bold]Troubleshooting tips:[/bold]")
        console.print("1. Run exercise_1_setup.py to validate your environment")
        console.print("2. Check your .env file configuration")
        console.print("3. Verify Azure authentication with 'az login'")
    finally:
        if chat_client and agent_name and chat_client.agent_id:
            if not (agent_id_source and agent_id_source.startswith("environment")):
                _persist_agent_identity(agent_name, chat_client.agent_id)
                console.print(
                    "📌 Tip: set AZURE_AI_AGENT_ID in your environment to reuse this agent across machines."
                )
        if credential is not None:
            await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
