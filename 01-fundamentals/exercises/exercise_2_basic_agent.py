"""
Exercise 2: Creating Your First Azure AI Agent

This exercise demonstrates how to create, test, and manage basic Azure AI agents.
You'll learn the fundamental workflow of agent creation and conversation handling.

Prerequisites:
- Complete exercise_1_setup.py successfully
- Environment variables configured in .env file
"""

import os
import time
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def create_basic_agent():
    """Create a simple Azure AI agent"""
    
    console.print(Panel.fit(
        "🤖 Creating Your First Azure AI Agent",
        style="bold blue"
    ))
    
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    console.print("\n🔧 [bold]Initializing Azure AI Project client...[/bold]")
    try:
        project_client = AIProjectClient(
            endpoint=os.getenv('PROJECT_ENDPOINT'),
            credential=DefaultAzureCredential()
        )
        console.print("✅ Client initialized successfully")
    except Exception as e:
        console.print(f"❌ Failed to initialize client: {e}")
        return None, None
    
    # Create agent with detailed instructions
    console.print("\n🎭 [bold]Creating agent...[/bold]")
    
    instructions = """
    You are Alex, a friendly and knowledgeable Azure AI assistant specializing in helping users learn Azure AI Foundry and agent development.
    
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
    """
    
    try:
        agent = project_client.agents.create_agent(
            model=os.getenv('MODEL_DEPLOYMENT_NAME'),
            name="Alex-Learning-Assistant",
            instructions=instructions.strip()
        )
        
        # Display agent details
        agent_table = Table()
        agent_table.add_column("Property", style="cyan")
        agent_table.add_column("Value", style="green")
        
        agent_table.add_row("Name", agent.name)
        agent_table.add_row("ID", agent.id)
        agent_table.add_row("Model", agent.model)
        agent_table.add_row("Created", str(agent.created_at) if hasattr(agent, 'created_at') else 'N/A')
        
        console.print(f"\n✅ [bold green]Agent created successfully![/bold green]")
        console.print(agent_table)
        
        return agent, project_client
        
    except Exception as e:
        console.print(f"❌ Failed to create agent: {e}")
        return None, None

def test_agent_conversation(agent, project_client):
    """Test the agent with a conversation"""
    
    console.print(f"\n💬 [bold]Testing conversation with {agent.name}...[/bold]")
    
    try:
        # Create a conversation thread
        thread = project_client.agents.create_thread()
        console.print(f"📞 Created conversation thread: [dim]{thread.id}[/dim]")
        
        # Test questions to ask the agent
        test_questions = [
            "Hello! I'm new to Azure AI agents. Can you explain what makes them so powerful for building AI applications?",
            "What are the key components I need to understand when building my first agent?",
            "Can you give me a practical example of when I would use an Azure AI agent versus a regular chatbot?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            console.print(f"\n🔄 [bold]Test Question {i}/{len(test_questions)}[/bold]")
            
            # Send user message
            message = project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=question
            )
            
            console.print(f"👤 [bold blue]User:[/bold blue] {question}")
            
            # Start agent run
            run = project_client.agents.create_run(
                thread_id=thread.id,
                agent_id=agent.id
            )
            
            # Wait for completion with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("🤖 Agent is thinking...", total=None)
                
                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
                    progress.update(task, description=f"🤖 Agent status: {run.status}")
            
            # Get and display response
            if run.status == "completed":
                messages = project_client.agents.list_messages(thread_id=thread.id)
                
                # Find the most recent assistant message
                for msg in messages.data:
                    if msg.role == "assistant" and msg.created_at > message.created_at:
                        response = msg.content[0].text.value
                        console.print(f"\n🤖 [bold green]Alex:[/bold green] {response}")
                        break
            else:
                console.print(f"❌ Run failed with status: {run.status}")
                if hasattr(run, 'last_error') and run.last_error:
                    console.print(f"Error details: {run.last_error}")
                break
            
            # Pause between questions
            if i < len(test_questions):
                console.print("\n" + "─" * 50)
        
        return thread
        
    except Exception as e:
        console.print(f"❌ Conversation test failed: {e}")
        return None

def demonstrate_agent_properties(agent):
    """Demonstrate different agent properties and capabilities"""
    
    console.print(f"\n🔍 [bold]Exploring agent properties...[/bold]")
    
    # Show agent details
    details_table = Table(title=f"Agent Details: {agent.name}")
    details_table.add_column("Property", style="cyan")
    details_table.add_column("Value", style="white")
    
    # Get all available properties
    properties = [
        ("ID", agent.id),
        ("Name", agent.name),
        ("Model", agent.model),
        ("Instructions Preview", agent.instructions[:100] + "..." if len(agent.instructions) > 100 else agent.instructions),
        ("Has Tools", "Yes" if hasattr(agent, 'tools') and agent.tools else "No"),
        ("Created At", str(agent.created_at) if hasattr(agent, 'created_at') else 'N/A'),
    ]
    
    for prop, value in properties:
        details_table.add_row(prop, str(value))
    
    console.print(details_table)

def cleanup_agent(agent, project_client):
    """Clean up created agent"""
    
    console.print(f"\n🧹 [bold]Cleaning up agent...[/bold]")
    
    try:
        project_client.agents.delete_agent(agent.id)
        console.print(f"✅ Agent '{agent.name}' deleted successfully")
    except Exception as e:
        console.print(f"⚠️ Failed to delete agent: {e}")
        console.print("You may need to manually delete it from the Azure AI Foundry portal")

def main():
    """Main exercise function"""
    
    try:
        # Step 1: Create agent
        agent, project_client = create_basic_agent()
        if not agent:
            return
        
        # Step 2: Explore agent properties
        demonstrate_agent_properties(agent)
        
        # Step 3: Test conversation
        thread = test_agent_conversation(agent, project_client)
        
        # Step 4: Show success message
        console.print(Panel.fit(
            "🎉 [bold green]Congratulations![/bold green]\n\n"
            "You've successfully:\n"
            "• Created your first Azure AI agent\n"
            "• Configured detailed instructions\n"
            "• Tested multi-turn conversations\n"
            "• Learned about agent properties\n\n"
            "🚀 Next: Learn about threads and runs in exercise_3_conversation.py",
            style="bold green",
            title="✅ SUCCESS"
        ))
        
        # Step 5: Cleanup
        cleanup_agent(agent, project_client)
        
        # Show learning tips
        console.print(Panel(
            "💡 [bold]Key Learnings:[/bold]\n\n"
            "1. [cyan]Agent Instructions[/cyan]: Detailed instructions create more consistent behavior\n"
            "2. [cyan]Conversation Flow[/cyan]: Thread → Message → Run → Response\n"
            "3. [cyan]Run States[/cyan]: Monitor 'queued', 'in_progress', 'completed' states\n"
            "4. [cyan]Error Handling[/cyan]: Always check run status before reading responses\n"
            "5. [cyan]Resource Management[/cyan]: Clean up agents to avoid hitting limits\n\n"
            "🎯 [bold]Try This:[/bold] Modify the agent instructions and see how it changes responses!",
            title="📚 Learning Summary"
        ))
        
    except KeyboardInterrupt:
        console.print("\n👋 Exercise interrupted by user")
        if 'agent' in locals() and agent:
            cleanup_agent(agent, project_client)
    except Exception as e:
        console.print(f"\n💥 [bold red]Unexpected error:[/bold red] {e}")
        console.print("\n💡 [bold]Troubleshooting tips:[/bold]")
        console.print("1. Run exercise_1_setup.py to validate your environment")
        console.print("2. Check your .env file configuration")
        console.print("3. Verify Azure authentication with 'az login'")

if __name__ == "__main__":
    main()
