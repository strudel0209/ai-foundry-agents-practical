# 3. Understanding Threads and Runs

In this lesson, you'll master the conversation flow in Azure AI Foundry agents through threads and runs - the core execution model that powers agent interactions.

## 🎯 Objectives

- Understand the thread and run execution model
- Create and manage conversation threads
- Monitor run states and handle different scenarios
- Implement proper polling and status handling
- Build conversation history management
- Handle tool execution during runs

## ⏱️ Estimated Time: 45 minutes

## 🧠 Key Concepts

### The Agent Execution Model

Azure AI Foundry agents use a sophisticated execution model:

```
User Message → Thread → Run → Agent Processing → Tool Calls → Response
```

### Core Components

1. **Thread**: A conversation session that maintains context
2. **Message**: Individual communications within a thread
3. **Run**: Agent activation to process thread messages
4. **Run Step**: Detailed execution steps during a run
5. **Tool Outputs**: Results from tool executions

### Run States

```
queued → in_progress → requires_action → completed
                    ↓
                   failed/cancelled/expired
```

## 🚀 Step-by-Step Implementation

### Step 1: Basic Thread and Run Operations

```python
# exercises/exercise_3_conversation.py
import os
import time
import asyncio
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

console = Console()

async def basic_conversation_flow():
    """Demonstrate basic thread and run operations"""
    
    load_dotenv()
    
    # Initialize client and create agent
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )
    
    # Create a simple agent for testing
    agent = project_client.agents.create_agent(
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),
        name="conversation-tester",
        instructions="You are a helpful assistant that provides clear, concise answers."
    )
    
    console.print(f"✅ Created agent: {agent.id}")
    
    try:
        # Step 1: Create a conversation thread
        thread = project_client.agents.threads.create()
        console.print(f"📞 Created thread: {thread.id}")
        
        # Step 2: Add a user message
        user_message = "Explain what Azure AI Foundry agents are in 3 sentences."
        
        message = project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        console.print(f"💬 Added message: {message.id}")
        
        # Step 3: Create and monitor a run
        run = project_client.agents.runs.create(
            thread_id=thread.id,
            agent_id=agent.id
        )
        console.print(f"🏃 Started run: {run.id}")
        
        # Step 4: Poll for completion
        await poll_run_completion(project_client, thread.id, run.id)
        
        # Step 5: Retrieve the response
        messages = project_client.agents.messages.list(thread_id=thread.id)
        
        console.print(Panel.fit(
            "💡 Conversation History",
            style="bold blue"
        ))
        
        for msg in reversed(messages):
            role_color = "green" if msg.role == "assistant" else "cyan"
            content = msg.content[0].text.value if msg.content else "No content"
            console.print(f"[{role_color}]{msg.role.title()}:[/{role_color}] {content}\n")
            
    finally:
        # Cleanup
        project_client.agents.delete_agent(agent.id)
        console.print("🧹 Cleaned up agent")

async def poll_run_completion(client, thread_id, run_id):
    """Poll run status with visual feedback"""
    
    status_table = Table()
    status_table.add_column("Status", style="cyan")
    status_table.add_column("Duration", style="green")
    status_table.add_column("Details", style="yellow")
    
    start_time = time.time()
    
    with Live(status_table, refresh_per_second=2, console=console) as live:
        while True:
            run = client.agents.runs.get(thread_id=thread_id, run_id=run_id)
            elapsed = time.time() - start_time
            
            status_table.add_row(
                run.status,
                f"{elapsed:.1f}s",
                f"Run ID: {run_id[:8]}..."
            )
            
            live.update(status_table)
            
            if run.status in ["completed", "failed", "cancelled", "expired"]:
                break
            
            await asyncio.sleep(1)
    
    console.print(f"✅ Run completed with status: [bold green]{run.status}[/bold green]")
    return run

if __name__ == "__main__":
    asyncio.run(basic_conversation_flow())
```

### Step 2: Advanced Run Monitoring

```python
def monitor_run_with_steps(client, thread_id, run_id):
    """Monitor run execution with detailed step tracking"""
    
    console.print("\n🔍 [bold]Monitoring run execution...[/bold]")
    
    while True:
        run = client.agents.runs.get(thread_id=thread_id, run_id=run_id)
        
        # Display current status
        status_color = {
            "queued": "yellow",
            "in_progress": "blue", 
            "requires_action": "magenta",
            "completed": "green",
            "failed": "red",
            "cancelled": "orange",
            "expired": "red"
        }.get(run.status, "white")
        
        console.print(f"Status: [{status_color}]{run.status}[/{status_color}]")
        
        # Get run steps for detailed tracking
        run_steps = client.agents.runs.steps.list(
            thread_id=thread_id,
            run_id=run_id
        )
        
        if run_steps.data:
            steps_table = Table()
            steps_table.add_column("Step", style="cyan")
            steps_table.add_column("Type", style="green") 
            steps_table.add_column("Status", style="yellow")
            steps_table.add_column("Details", style="white")
            
            for step in run_steps.data:
                step_type = step.type
                step_status = step.status
                
                # Extract step details based on type
                details = ""
                if hasattr(step, 'step_details'):
                    if step.type == "message_creation":
                        details = f"Message: {step.step_details.message_creation.message_id[:8]}..."
                    elif step.type == "tool_calls":
                        tool_calls = step.step_details.tool_calls
                        details = f"{len(tool_calls)} tool call(s)"
                
                steps_table.add_row(
                    step.id[:8] + "...",
                    step_type,
                    step_status,
                    details
                )
            
            console.print(steps_table)
        
        if run.status in ["completed", "failed", "cancelled", "expired"]:
            break
            
        time.sleep(2)
    
    return run
```

### Step 3: Handling Tool Execution

```python
def handle_tool_execution_run(client, agent_with_tools, thread_id):
    """Demonstrate handling runs that require tool execution"""
    
    # Add message that will trigger tool use
    client.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content="What's the current time and calculate 25 * 47?"
    )
    
    # Create run
    run = client.agents.runs.create(
        thread_id=thread_id,
        agent_id=agent_with_tools.id
    )
    
    console.print(f"🏃 Started run with tools: {run.id}")
    
    while True:
        run = client.agents.runs.get(thread_id=thread_id, run_id=run.id)
        
        console.print(f"Run status: {run.status}")
        
        if run.status == "requires_action":
            console.print("🔧 Run requires action - handling tool calls...")
            
            # Get required action details
            if hasattr(run, 'required_action') and run.required_action:
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                
                console.print(f"Processing {len(tool_calls)} tool call(s):")
                
                tool_outputs = []
                for tool_call in tool_calls:
                    console.print(f"  - {tool_call.function.name}({tool_call.function.arguments})")
                    
                    # Simulate tool execution (in real scenario, execute actual functions)
                    if tool_call.function.name == "get_current_time":
                        output = f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    elif tool_call.function.name == "calculate":
                        # Parse arguments and calculate
                        import json
                        args = json.loads(tool_call.function.arguments)
                        result = eval(f"{args['expression']}")  # Note: Use safely in production
                        output = f"Result: {result}"
                    else:
                        output = "Tool execution completed"
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": output
                    })
                
                # Submit tool outputs
                client.agents.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                
                console.print("✅ Submitted tool outputs")
        
        elif run.status in ["completed", "failed", "cancelled", "expired"]:
            break
        
        time.sleep(2)
    
    return run
```

### Step 4: Conversation History Management

```python
class ConversationManager:
    """Manage conversation history and context"""
    
    def __init__(self, project_client):
        self.client = project_client
        self.conversation_history = []
    
    def add_user_message(self, thread_id, content):
        """Add user message and track in history"""
        message = self.client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=content
        )
        
        self.conversation_history.append({
            "role": "user",
            "content": content,
            "timestamp": time.time(),
            "message_id": message.id
        })
        
        return message
    
    def process_agent_response(self, thread_id, run_id):
        """Process agent response and update history"""
        
        # Get the latest messages after run completion
        messages = self.client.agents.list_messages(thread_id=thread_id)
        
        # Find new assistant messages
        for message in messages.data:
            if message.role == "assistant":
                # Check if this message is new (not in our history)
                if not any(h.get("message_id") == message.id for h in self.conversation_history):
                    content = message.content[0].text.value if message.content else ""
                    
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": content,
                        "timestamp": time.time(),
                        "message_id": message.id,
                        "run_id": run_id
                    })
    
    def get_conversation_summary(self):
        """Get formatted conversation summary"""
        summary_table = Table()
        summary_table.add_column("Role", style="cyan")
        summary_table.add_column("Content", style="white", max_width=60)
        summary_table.add_column("Time", style="green")
        
        for entry in self.conversation_history:
            role_color = "green" if entry["role"] == "assistant" else "blue"
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"]))
            
            summary_table.add_row(
                f"[{role_color}]{entry['role'].title()}[/{role_color}]",
                entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
                timestamp
            )
        
        return summary_table
    
    def export_conversation(self, filename):
        """Export conversation to JSON file"""
        import json
        
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        console.print(f"💾 Exported conversation to {filename}")
```

## 🎯 Exercises

### Exercise A: Multi-Turn Conversation

Create a conversation that spans multiple turns and demonstrates context retention:

1. Ask the agent to remember a specific piece of information
2. Have a few exchanges about other topics  
3. Reference the original information to test memory

### Exercise B: Error Handling

Implement robust error handling for:
- Run timeouts
- Failed runs  
- Connection issues
- Invalid tool outputs

### Exercise C: Performance Monitoring

Build a system to track:
- Average response times
- Token usage per run
- Tool execution frequency
- Error rates

## 🔍 Best Practices

### Thread Management

1. **Reuse Threads**: Keep conversations in the same thread for context
2. **Clean Up**: Delete threads when conversations are complete
3. **Limit Length**: Monitor thread length to avoid token limits
4. **Backup Context**: Save important conversation state externally

### Run Monitoring

1. **Implement Timeouts**: Don't wait indefinitely for runs
2. **Handle All States**: Prepare for failed, cancelled, and expired runs
3. **Log Details**: Capture run steps for debugging
4. **Retry Logic**: Implement retry for transient failures

### Tool Execution

1. **Validate Inputs**: Check tool call arguments before execution
2. **Error Recovery**: Handle tool execution failures gracefully
3. **Security**: Sanitize and validate all tool outputs
4. **Performance**: Monitor tool execution times

## 🔧 Troubleshooting

### Common Issues

**Run stuck in "queued" status:**
- Check model deployment availability
- Verify quota limits
- Try with different model

**"requires_action" handling fails:**
- Ensure tool output format is correct
- Check tool_call_id matches exactly
- Validate tool output content

**Messages not appearing:**
- Wait for run completion before fetching messages
- Check message ordering (latest first)
- Verify thread_id is correct

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Thread Lifecycle**: How to create, use, and manage conversation threads
2. **Run States**: Different run states and how to handle each
3. **Tool Integration**: How tools are executed within runs
4. **Context Management**: Maintaining conversation history and context
5. **Error Handling**: Robust patterns for handling failures

## ➡️ Next Step

Once you've mastered threads and runs, proceed to [Agent Lifecycle Management](./04-lifecycle.md) to learn about managing agents throughout their lifetime.

---

**💡 Pro Tip:** Always implement proper cleanup in your applications. Unused threads and agents consume resources and count against quotas.
