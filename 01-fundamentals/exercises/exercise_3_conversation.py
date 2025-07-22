"""
Exercise 3: Advanced Conversation Management

This exercise demonstrates advanced thread and run management patterns
in Azure AI Foundry agents, including tool execution, error handling,
and conversation history management.

Prerequisites:
- Complete exercise_2_basic_agent.py successfully
- Agent creation working properly
"""

import os
import time
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class ConversationManager:
    """Advanced conversation management with history tracking"""
    
    def __init__(self, project_client: AIProjectClient):
        self.client = project_client
        self.conversation_history = []
        self.active_threads = {}
        
    def create_conversation(self, name: str) -> str:
        """Create a new conversation thread"""
        thread = self.client.agents.threads.create()
        self.active_threads[name] = {
            "thread_id": thread.id,
            "created_at": time.time(),
            "message_count": 0
        }
        return thread.id
    
    def add_message(self, thread_id: str, content: str, role: str = "user") -> Dict:
        """Add message to thread and track in history"""
        message = self.client.agents.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
        
        history_entry = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "message_id": message.id,
            "thread_id": thread_id
        }
        
        self.conversation_history.append(history_entry)
        
        # Update thread stats
        for thread_name, thread_info in self.active_threads.items():
            if thread_info["thread_id"] == thread_id:
                thread_info["message_count"] += 1
                break
        
        return history_entry
    
    async def execute_run_with_monitoring(self, thread_id: str, agent_id: str) -> Dict:
        """Execute agent run with comprehensive monitoring"""
        
        console.print(f"\n🏃 [bold]Starting agent run...[/bold]")
        
        # Create run
        run = self.client.agents.runs.create(
            thread_id=thread_id,
            agent_id=agent_id
        )
        
        console.print(f"Run ID: [dim]{run.id}[/dim]")
        
        # Monitor with live table
        status_table = Table()
        status_table.add_column("Status", style="cyan")
        status_table.add_column("Duration", style="green")
        status_table.add_column("Steps", style="yellow")
        status_table.add_column("Details", style="white")
        
        start_time = time.time()
        step_count = 0
        
        with Live(status_table, refresh_per_second=2, console=console) as live:
            while True:
                run = self.client.agents.runs.get(thread_id=thread_id, run_id=run.id)
                elapsed = time.time() - start_time
                
                # Get run steps
                try:
                    run_steps = self.client.agents.runs.steps.list(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    step_count = len(run_steps.data) if run_steps.data else 0
                except:
                    step_count = 0
                
                # Update status table
                status_table.add_row(
                    f"[bold]{run.status}[/bold]",
                    f"{elapsed:.1f}s",
                    str(step_count),
                    self._get_run_details(run)
                )
                
                live.update(status_table)
                
                # Handle special states
                if run.status == "requires_action":
                    await self._handle_tool_execution(thread_id, run.id, run)
                elif run.status in ["completed", "failed", "cancelled", "expired"]:
                    break
                
                await asyncio.sleep(1)
        
        # Update conversation history with assistant response
        if run.status == "completed":
            await self._update_history_with_response(thread_id, run.id)
        
        console.print(f"✅ Run completed: [bold green]{run.status}[/bold green]")
        
        return {
            "run_id": run.id,
            "status": run.status,
            "duration": time.time() - start_time,
            "step_count": step_count
        }
    
    async def _handle_tool_execution(self, thread_id: str, run_id: str, run) -> None:
        """Handle tool execution during run"""
        
        console.print("🔧 [bold yellow]Handling tool execution...[/bold yellow]")
        
        if not hasattr(run, 'required_action') or not run.required_action:
            console.print("❌ No required action found")
            return
        
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        console.print(f"📋 Processing {len(tool_calls)} tool call(s)")
        
        tool_outputs = []
        
        for i, tool_call in enumerate(tool_calls, 1):
            console.print(f"  {i}. [cyan]{tool_call.function.name}[/cyan]")
            console.print(f"     Args: [dim]{tool_call.function.arguments}[/dim]")
            
            # Simulate tool execution (replace with actual tool logic)
            try:
                output = await self._execute_tool(tool_call)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
                console.print(f"     ✅ [green]Success[/green]: {output[:50]}...")
                
            except Exception as e:
                error_output = f"Error executing tool: {str(e)}"
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": error_output
                })
                console.print(f"     ❌ [red]Error[/red]: {str(e)}")
        
        # Submit tool outputs
        if tool_outputs:
            self.client.agents.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            console.print("📤 Submitted tool outputs")
    
    async def _execute_tool(self, tool_call) -> str:
        """Execute individual tool call"""
        
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        
        # Example tool implementations
        if function_name == "get_current_time":
            return time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        elif function_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # Simple calculator (use safely in production)
                result = eval(expression.replace("^", "**"))
                return f"Result: {result}"
            except:
                return "Error: Invalid expression"
        
        elif function_name == "search_web":
            query = arguments.get("query", "")
            return f"Search results for '{query}': [Simulated search results]"
        
        else:
            return f"Tool '{function_name}' executed successfully"
    
    async def _update_history_with_response(self, thread_id: str, run_id: str) -> None:
        """Update history with assistant's response"""
        
        # Get latest messages
        messages = self.client.agents.messages.list(thread_id=thread_id)
        
        # Find new assistant messages not in history
        for message in messages:
            if message.role == "assistant":
                if not any(h.get("message_id") == message.id for h in self.conversation_history):
                    content = message.content[0].text.value if message.content else ""
                    
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": content,
                        "timestamp": time.time(),
                        "message_id": message.id,
                        "thread_id": thread_id,
                        "run_id": run_id
                    })
    
    def _get_run_details(self, run) -> str:
        """Get run details for display"""
        details = []
        
        if hasattr(run, 'last_error') and run.last_error:
            details.append(f"Error: {run.last_error.message}")
        
        if hasattr(run, 'required_action') and run.required_action:
            action_type = type(run.required_action).__name__
            details.append(f"Action: {action_type}")
        
        return " | ".join(details) if details else "Processing..."
    
    def display_conversation_history(self, thread_id: str = None) -> None:
        """Display formatted conversation history"""
        
        # Filter by thread if specified
        messages = self.conversation_history
        if thread_id:
            messages = [m for m in messages if m.get("thread_id") == thread_id]
        
        if not messages:
            console.print("📭 No conversation history found")
            return
        
        console.print(Panel.fit(
            f"💬 Conversation History ({len(messages)} messages)",
            style="bold blue"
        ))
        
        for i, msg in enumerate(messages, 1):
            role_color = "green" if msg["role"] == "assistant" else "cyan"
            timestamp = time.strftime("%H:%M:%S", time.localtime(msg["timestamp"]))
            
            content = msg["content"]
            if len(content) > 100:
                content = content[:97] + "..."
            
            console.print(f"[dim]{i:2d}.[/dim] [{role_color}]{msg['role'].title()}[/{role_color}] "
                         f"[dim]({timestamp})[/dim]: {content}")
            
            if i < len(messages):
                console.print()
    
    def export_conversation(self, filename: str, thread_id: str = None) -> None:
        """Export conversation to JSON file"""
        
        messages = self.conversation_history
        if thread_id:
            messages = [m for m in messages if m.get("thread_id") == thread_id]
        
        export_data = {
            "exported_at": time.time(),
            "thread_id": thread_id,
            "message_count": len(messages),
            "messages": messages,
            "thread_stats": self.active_threads
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"💾 Exported {len(messages)} messages to {filename}")

async def get_or_create_agent(project_client: AIProjectClient, agent_name: str):
    """Gets an agent by name or creates it if it doesn't exist."""
    
    # List all agents in the project
    agents_list = project_client.agents.list_agents()
    
    # Check if an agent with the given name already exists
    for agent in agents_list:
        if agent.name == agent_name:
            console.print(f"🤖 Found existing agent: [bold]'{agent.name}'[/bold] (ID: {agent.id})")
            return agent
            
    # If no agent is found, create a new one
    console.print(f"🤔 Agent '{agent_name}' not found, creating a new one...")
    return await create_test_agent_with_tools(project_client, agent_name)

async def create_test_agent_with_tools(project_client: AIProjectClient, agent_name: str):
    """Create a test agent with basic tools for demonstration"""
    
    # Define simple tools for testing
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current date and time",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "calculate",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
    
    agent = project_client.agents.create_agent(
        name=agent_name,
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),
        instructions="""
        You are a helpful assistant with access to tools for time and calculations.
        
        When users ask for the time, use the get_current_time tool.
        When users ask for calculations, use the calculate tool.
        
        Always be friendly and explain what you're doing when using tools.
        """,
        tools=tools
    )
    
    console.print(f"🤖 Created agent with tools: {agent.id}")
    return agent

async def demo_conversation_scenarios(manager: ConversationManager, agent_id: str):
    """Demonstrate various conversation scenarios"""
    
    scenarios = [
        {
            "name": "Basic Q&A",
            "messages": [
                "Hello! Can you introduce yourself?",
                "What can you help me with?"
            ]
        },
        {
            "name": "Tool Usage",
            "messages": [
                "What time is it right now?",
                "Can you calculate 25 * 47 + 18?",
                "What's the square root of 144?"
            ]
        },
        {
            "name": "Context Retention",
            "messages": [
                "My name is Alice and I work as a data scientist.",
                "I'm working on a machine learning project with Python.",
                "Can you remember what I told you about myself?",
                "What programming language did I mention?"
            ]
        }
    ]
    
    for scenario in scenarios:
        console.print(Panel.fit(
            f"🎭 Scenario: {scenario['name']}",
            style="bold magenta"
        ))
        
        # Create new thread for this scenario
        thread_id = manager.create_conversation(scenario['name'])
        
        for message in scenario['messages']:
            console.print(f"\n👤 [cyan]User:[/cyan] {message}")
            
            # Add user message
            manager.add_message(thread_id, message)
            
            # Execute agent run
            run_result = await manager.execute_run_with_monitoring(thread_id, agent_id)
            
            # Brief pause between messages
            await asyncio.sleep(1)
        
        # Show conversation for this scenario
        console.print(f"\n📝 [bold]Conversation Summary for {scenario['name']}:[/bold]")
        manager.display_conversation_history(thread_id)
        
        # Export this conversation
        export_filename = f"conversation_{scenario['name'].lower().replace(' ', '_')}.json"
        manager.export_conversation(export_filename, thread_id)
        
        console.print("\n" + "="*60 + "\n")

async def main():
    """Main demonstration function"""
    
    console.print(Panel.fit(
        "🚀 Azure AI Foundry Advanced Conversation Demo",
        style="bold blue"
    ))
    
    load_dotenv()
    
    # Initialize client
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )
    
    # Create conversation manager
    manager = ConversationManager(project_client)
    
    try:
        # Get or create the test agent
        agent = await get_or_create_agent(project_client, "conversation-demo-agent")
        
        # Run demonstration scenarios
        await demo_conversation_scenarios(manager, agent.id)
        
        # Show overall statistics
        console.print(Panel.fit(
            "📊 Session Statistics",
            style="bold green"
        ))
        
        stats_table = Table()
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Messages", str(len(manager.conversation_history)))
        stats_table.add_row("Active Threads", str(len(manager.active_threads)))
        stats_table.add_row("User Messages", str(len([m for m in manager.conversation_history if m["role"] == "user"])))
        stats_table.add_row("Assistant Messages", str(len([m for m in manager.conversation_history if m["role"] == "assistant"])))
        
        console.print(stats_table)
        
        # Export full session
        manager.export_conversation("full_session_export.json")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        
    # The finally block with cleanup is commented out to allow agent persistence
    # finally:
    #     # Cleanup
    #     try:
    #         project_client.agents.delete(name=agent.name)
    #         console.print("🧹 Cleaned up test agent")
    #     except:
    #         pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Demo interrupted by user")
    except Exception as e:
        console.print(f"\n💥 [bold red]Unexpected error:[/bold red] {e}")
