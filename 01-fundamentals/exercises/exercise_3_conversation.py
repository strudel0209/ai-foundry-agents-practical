#!/usr/bin/env python3
"""
Exercise 3: Understanding Threads and Conversation History

This exercise demonstrates:
1. How threads maintain conversation history
2. How agents remember context across multiple interactions
3. How to manage and inspect thread state
"""

import os
import time
import textwrap
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()
load_dotenv()

class ConversationDemo:
    def __init__(self):
        """Initialize the conversation demo with Azure AI client"""
        self.project_client = AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        self.agents_client = AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        self.agent = None                 # persisted agent (AIProjectClient)
        self.runtime_agent = None         # runtime assistant (AgentsClient) — starts with 'asst_...'
        self.thread = None
    
    def find_existing_agent(self, agent_name):
        """Check if an agent with the given name already exists"""
        try:
            console.print(f"🔍 Checking for existing agent '{agent_name}'...")
            
            # NOTE: this is the AIProjectClient Agents – for persistence in Foundry
            agents = self.project_client.agents.list(limit=100)
            
            # Search for agent by name
            for agent in agents:
                if agent.name == agent_name:
                    console.print(f"✅ Found existing agent: {agent.name} (ID: {agent.id})")
                    return agent
            
            console.print(f"ℹ️ No existing agent found with name '{agent_name}'")
            return None
            
        except Exception as e:
            console.print(f"⚠️ Error checking for existing agents: {e}")
            return None
    
    def create_agent(self):
        """Create an agent optimized for demonstrating conversation memory"""
        # kept for backwards compatibility — delegate to get_or_create_agent
        return self.get_or_create_agent()
    
    def get_or_create_agent(self, agent_name: str = "conversation-memory-demo", instructions: str | None = None):
        """
        Find an existing agent by name and return it, otherwise create a new one.
        This uses AIProjectClient so the agent is visible in Azure AI Foundry.
        Also ensures a runtime assistant exists in AgentsClient (id begins with 'asst')
        """
        # allow callers to pass custom instructions, but default to the demo instructions
        if instructions is None:
            instructions = """
        You are a helpful AI assistant that demonstrates conversation memory.
        Key behaviors:
        - Remember all previous messages in our conversation
        - Reference earlier topics when relevant
        - Keep track of user preferences and information shared
        - Acknowledge when you're recalling something from earlier
        
        When asked about conversation history, provide specific examples
        of what you remember from our chat.
        """
        
        instructions = textwrap.dedent(instructions).strip()
        
        # First check if persisted agent already exists in Foundry
        existing_agent = self.find_existing_agent(agent_name)
        if existing_agent:
            self.agent = existing_agent
            console.print(f"♻️ Reusing existing agent: {self.agent.name} (ID: {self.agent.id})")
        else:
            console.print(f"🎭 Creating new agent '{agent_name}'...")
            try:
                definition = PromptAgentDefinition(
                    model=os.environ["MODEL_DEPLOYMENT_NAME"],
                    instructions=instructions
                )
                self.agent = self.project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=definition
                )
                console.print(f"✅ Created new agent: {self.agent.name} (ID: {self.agent.id})")
            except Exception as e:
                console.print(f"❌ Error creating agent: {e}")
                raise

        # --- NEW: Ensure a runtime assistant exists in Agents service ---
        try:
            # Try to find runtime assistant with same name
            runtime_candidates = self.agents_client.list_agents(limit=100)
            for r in runtime_candidates:
                if getattr(r, "name", None) == agent_name:
                    self.runtime_agent = r
                    console.print(f"♻️ Reusing runtime assistant: {self.runtime_agent.name} (ID: {self.runtime_agent.id})")
                    break

            # If not found, create runtime assistant (this returns id like 'asst_...')
            if not self.runtime_agent:
                console.print(f"⚙️ Creating runtime assistant for agent '{agent_name}'...")
                self.runtime_agent = self.agents_client.create_agent(
                    model=os.environ["MODEL_DEPLOYMENT_NAME"],
                    name=agent_name,
                    instructions=instructions,
                )
                console.print(f"✅ Created runtime assistant: {self.runtime_agent.name} (ID: {self.runtime_agent.id})")

        except Exception as e:
            console.print(f"⚠️ Error ensuring runtime assistant: {e}")
            raise

        return self.agent

    def demonstrate_single_thread_conversation(self):
        """Show how a single thread maintains conversation history"""
        console.print(Panel.fit(
            "🧵 [bold]Demo 1: Single Thread Conversation[/bold]\n"
            "Showing how context is maintained across messages",
            style="blue"
        ))

        # Use AgentsClient for thread/message/run operations
        with self.agents_client:
            # Create one thread for the entire conversation
            self.thread = self.agents_client.threads.create()
            console.print(f"📝 Created thread: {self.thread.id}\n")

            conversation_flow = [
                "Hi! My name is Alice and I love hiking.",
                "What's your favorite outdoor activity?",
                "Can you remind me what my name is?",
                "What did I tell you I enjoy doing?",
                "Based on what you know about me, what would you recommend I do this weekend?"
            ]

            for i, message in enumerate(conversation_flow, 1):
                console.print(f"\n[bold cyan]Turn {i}:[/bold cyan]")
                console.print(f"👤 User: {message}")

                # Add message to thread
                self.agents_client.messages.create(
                    thread_id=self.thread.id,
                    role="user",
                    content=message,
                )

                # Create and process run for this thread — use runtime assistant id (asst_...)
                run = self.agents_client.runs.create_and_process(
                    thread_id=self.thread.id,
                    agent_id=self.runtime_agent.id,
                )

                if run.status == "failed":
                    console.print(f"⚠️ Run failed: {run.last_error}")
                    continue

                if run.status == "completed":
                    # List all messages for this thread
                    messages = self.agents_client.messages.list(
                        thread_id=self.thread.id
                    )

                    # Find the latest assistant message
                    for msg in messages:
                        if msg.role == "assistant":
                            response = self._extract_message_content(msg)
                            console.print(f"🤖 Assistant: {response}")
                            break

                time.sleep(1)

        self._show_thread_summary()

    def demonstrate_multiple_threads_isolation(self):
        """Show how different threads don't share context"""
        console.print(Panel.fit(
            "🧵 [bold]Demo 2: Thread Isolation[/bold]\n"
            "Showing how different threads maintain separate contexts",
            style="yellow"
        ))

        with self.agents_client:
            thread1 = self.agents_client.threads.create()
            thread2 = self.agents_client.threads.create()

            console.print(f"📝 Created Thread 1: {thread1.id}")
            console.print(f"📝 Created Thread 2: {thread2.id}\n")

            console.print("[bold]Thread 1 Conversation:[/bold]")
            self._send_message_to_thread(
                thread1.id,
                "Hi, I'm Bob and I love cooking Italian food."
            )

            console.print("\n[bold]Thread 2 Conversation:[/bold]")
            self._send_message_to_thread(
                thread2.id,
                "Hello, I'm Carol and I enjoy painting landscapes."
            )

            console.print("\n[bold]Back to Thread 1:[/bold]")
            self._send_message_to_thread(
                thread1.id,
                "What do you remember about me?"
            )

            console.print("\n[bold]Back to Thread 2:[/bold]")
            self._send_message_to_thread(
                thread2.id,
                "What do you remember about me?"
            )

        console.print("\n💡 [bold]Note:[/bold] Each thread maintains its own conversation history!")

    def demonstrate_thread_persistence(self):
        """Show how to resume a conversation using thread ID"""
        console.print(Panel.fit(
            "🧵 [bold]Demo 3: Thread Persistence[/bold]\n"
            "Showing how to resume conversations using thread IDs",
            style="green"
        ))

        if not self.thread:
            console.print("❌ No existing thread to resume. Run Demo 1 first!")
            return

        thread_id = self.thread.id
        console.print(f"📎 Resuming thread: {thread_id}\n")

        console.print("[dim]Simulating user returning to conversation...[/dim]\n")
        time.sleep(2)

        self._send_message_to_thread(
            thread_id,
            "Hi again! Do you remember our conversation from earlier? What did we discuss?"
        )

        self._show_thread_history(thread_id)

    def _send_message_to_thread(self, thread_id, content):
        """Helper to send a message to a specific thread"""
        console.print(f"👤 User: {content}")

        self.agents_client.messages.create(
            thread_id=thread_id,
            role="user",
            content=content,
        )

        run = self.agents_client.runs.create_and_process(
            thread_id=thread_id,
            agent_id=self.runtime_agent.id,
        )

        if run.status == "failed":
            console.print(f"⚠️ Run failed: {run.last_error}")
            return

        if run.status == "completed":
            messages = self.agents_client.messages.list(thread_id=thread_id)
            for msg in messages:
                if msg.role == "assistant":
                    response = self._extract_message_content(msg)
                    console.print(f"🤖 Assistant: {response}")
                    break

    def _extract_message_content(self, message):
        """Extract content from message object (AgentsClient message model)"""
        if hasattr(message, "content") and message.content:
            # In Agents SDK, content is typically a list of text/other blocks
            if isinstance(message.content, list) and len(message.content) > 0:
                first = message.content[0]
                # Text block
                if hasattr(first, "text") and first.text and hasattr(first.text, "value"):
                    return first.text.value
            return str(message.content)
        return "No content"
    
    def _show_thread_summary(self):
        """Display a summary of the current thread"""
        if not self.thread:
            return

        with self.agents_client:
            messages = self.agents_client.messages.list(thread_id=self.thread.id)

            table = Table(title=f"Thread Summary (ID: {self.thread.id[:8]}...)")
            table.add_column("Turn", style="cyan")
            table.add_column("Role", style="green")
            table.add_column("Message Preview", style="white")

            turn = 1
            for msg in reversed(list(messages)):
                content = self._extract_message_content(msg)
                preview = content[:50] + "..." if len(content) > 50 else content
                table.add_row(str(turn), msg.role.capitalize(), preview)
                turn += 1

            console.print("\n")
            console.print(table)

    def _show_thread_history(self, thread_id):
        """Display full conversation history for a thread"""
        console.print(f"\n📜 [bold]Full Thread History[/bold]")
        console.print(f"Thread ID: {thread_id}\n")

        with self.agents_client:
            messages = self.agents_client.messages.list(thread_id=thread_id)

            for msg in reversed(list(messages)):
                role_emoji = "👤" if msg.role == "user" else "🤖"
                content = self._extract_message_content(msg)
                console.print(f"{role_emoji} [bold]{msg.role.capitalize()}:[/bold] {content}")
                console.print()

    def cleanup(self):
        """Clean up resources"""
        if self.agent or self.runtime_agent:
            console.print(f"\n🧹 Cleaning up resources:")
        # Delete persisted agent from project (Foundry)
        if self.agent:
            try:
                with self.project_client:
                    self.project_client.agents.delete_agent(self.agent.id)
                    console.print(f"🗑️ Deleted persisted agent: {self.agent.id}")
            except Exception as e:
                console.print(f"⚠️ Error deleting persisted agent: {e}")
                console.print("You may need to manually delete it from the Azure AI Foundry portal")

        # Delete runtime assistant if created by this script
        if self.runtime_agent:
            try:
                with self.agents_client:
                    self.agents_client.delete_agent(self.runtime_agent.id)
                    console.print(f"🗑️ Deleted runtime assistant: {self.runtime_agent.id}")
            except Exception as e:
                console.print(f"⚠️ Error deleting runtime assistant: {e}")
                console.print("You may need to manually delete the runtime assistant in the Agents service")


def main():
    """Run the conversation history demonstrations"""
    console.print(Panel.fit(
        "🎓 [bold]Exercise 3: Threads and Conversation History[/bold]\n"
        "Learn how Azure AI Agents maintain context and memory",
        style="bold blue"
    ))
    
    demo = ConversationDemo()
    
    try:
        # Create the agent once (or reuse existing)
        demo.create_agent()
        
        # Demo 1: Single thread with conversation history
        demo.demonstrate_single_thread_conversation()
        input("\n➡️  Press Enter to continue to Demo 2...")
        
        # Demo 2: Multiple threads showing isolation
        demo.demonstrate_multiple_threads_isolation()
        input("\n➡️  Press Enter to continue to Demo 3...")
        
        # Demo 3: Thread persistence
        demo.demonstrate_thread_persistence()
        
        # Learning summary
        console.print(Panel(
            "🎯 [bold]Key Takeaways:[/bold]\n\n"
            "1. 🧵 **Threads** = Conversation sessions that maintain history\n"
            "2. 💬 **Messages** = Individual interactions stored in threads\n"
            "3. 🏃 **Runs** = Executions that process messages and generate responses\n"
            "4. 🔒 **Isolation** = Each thread has its own separate context\n"
            "5. 💾 **Persistence** = Threads can be resumed using their IDs\n\n"
            "💡 **Best Practice**: Use one thread per conversation session!",
            title="✅ Learning Summary",
            style="bold green"
        ))
        
    except Exception as e:
        console.print(f"❌ Error: {e}")
    finally:
        # Ask user if they want to keep the agent for inspection
        console.print("\n" + "=" * 50)
        keep_agent = input("💭 Keep agent for inspection? (y/N): ").strip().lower()
        
        if keep_agent != 'y':
            demo.cleanup()
        else:
            console.print("\n💡 Agent kept alive for inspection. Remember to clean up manually!")
            if demo.agent:
                console.print(f"   Agent ID: {demo.agent.id}")
                console.print(f"   Agent Name: {demo.agent.name}")


if __name__ == "__main__":
    main()