# 2. Creating Your First Agent

In this lesson, you'll learn how to create your first Azure AI Foundry agent. We'll cover the basic concepts, walk through the code step-by-step, and create a functional agent that can engage in conversations.

## 🎯 Objectives

- Understand Azure AI agent architecture
- Initialize the Azure AI Project client
- Create your first agent with custom instructions
- Test basic agent functionality
- Handle agent responses and conversations

## ⏱️ Estimated Time: 45 minutes

## 🧠 Key Concepts

### What is an Azure AI Agent?

An Azure AI Agent is a custom AI assistant that:
- Uses large language models (like gpt-4o-mini) as its reasoning engine
- Follows specific instructions that define its behavior and personality
- Can use tools to extend its capabilities (files, search, functions, etc.)
- Maintains conversation context through threads
- Executes tasks through runs

### Agent Components

1. **Instructions**: System prompts that define the agent's role and behavior
2. **Model**: The underlying LLM (e.g., gpt-4o-mini, gpt-4o-mini-mini)
3. **Tools**: Optional capabilities like code execution, file search, or custom functions
4. **Name**: A friendly identifier for your agent

### Client Architecture

```
AIProjectClient
├── agents (AgentsClient)
│   ├── create()
│   ├── list_agents()
│   ├── get()
│   ├── update()
│   └── delete()
├── threads
│   └── create()
└── runs
    ├── create()
    └── get()
```

## 🚀 Step-by-Step Implementation

### Step 1: Basic Agent Creation

Let's start with the simplest possible agent:

```python
# exercises/exercise_2_basic_agent.py
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

def create_basic_agent():
    """Create a basic Azure AI agent"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize the Azure AI Project client
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )
    
    # Create a basic agent
    agent = project_client.agents.create_agent(
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),  # e.g., "gpt-4o-mini"
        name="my-first-agent",
        instructions="You are a helpful assistant that provides clear and concise answers."
    )
    
    print(f"✅ Created agent with ID: {agent.id}")
    print(f"📝 Agent name: {agent.name}")
    print(f"🤖 Model: {agent.model}")
    print(f"📋 Instructions: {agent.instructions}")
    
    return agent, project_client

if __name__ == "__main__":
    agent, client = create_basic_agent()
```

### Step 2: Enhanced Agent with Better Instructions

Now let's create a more sophisticated agent with detailed instructions:

```python
def create_enhanced_agent():
    """Create an agent with more detailed instructions"""
    
    load_dotenv()
    
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )
    
    # Define detailed instructions
    instructions = """
    You are Alex, a knowledgeable and friendly Azure AI assistant.
    
    Your role:
    - Help users learn Azure AI Foundry and agent development
    - Provide clear, step-by-step explanations
    - Include practical examples in your responses
    - Be encouraging and supportive of learning
    
    Communication style:
    - Use a warm and professional tone
    - Break down complex concepts into simple terms
    - Ask clarifying questions when needed
    - Provide actionable next steps
    
    When helping with code:
    - Explain what each part does
    - Suggest best practices
    - Point out potential issues or improvements
    """
    
    agent = project_client.agents.create_agent(
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),
        name="Alex-Learning-Assistant",
        instructions=instructions.strip()
    )
    
    print(f"✅ Created enhanced agent: {agent.name}")
    print(f"🆔 Agent ID: {agent.id}")
    
    return agent, project_client
```

### Step 3: Testing Your Agent

Now let's test our agent by having a conversation:

```python
import time

def test_agent_conversation(agent, project_client):
    """Test the agent with a simple conversation"""
    
    print(f"\n🧪 Testing agent: {agent.name}")
    
    # Create a conversation thread
    thread = project_client.agents.threads.create()
    print(f"📞 Created conversation thread: {thread.id}")
    
    # Add a message to the thread
    user_message = "Hello! Can you explain what an Azure AI agent is?"
    
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    print(f"💬 User: {user_message}")
    
    # Create and run the agent
    run = project_client.agents.runs.create(
        thread_id=thread.id,
        agent_id=agent.id
    )
    print(f"🏃 Started run: {run.id}")
    
    # Wait for the run to complete
    while run.status in ["queued", "in_progress"]:
        print(f"⏳ Run status: {run.status}")
        time.sleep(2)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
    
    print(f"✅ Run completed with status: {run.status}")
    
    # Get the assistant's response
    if run.status == "completed":
        messages = project_client.agents.messages.list(thread_id=thread.id)
        
        # Find the assistant's response (most recent message)
        for message in messages:
            if message.role == "assistant":
                response = message.content[0].text.value
                print(f"🤖 Assistant: {response}")
                break
    else:
        print(f"❌ Run failed with status: {run.status}")
        if hasattr(run, 'last_error') and run.last_error:
            print(f"Error: {run.last_error}")
    
    return thread
```

### Step 4: Complete Example

Here's the complete working example:

```python
# exercises/exercise_2_basic_agent.py
import os
import time
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from rich.console import Console
from rich.panel import Panel

console = Console()

def create_and_test_agent():
    """Complete example: Create and test an Azure AI agent"""
    
    # Load environment variables
    load_dotenv()
    
    console.print(Panel.fit(
        "🤖 Creating Your First Azure AI Agent",
        style="bold blue"
    ))
    
    # Initialize client
    console.print("\n🔧 [bold]Initializing Azure AI Project client...[/bold]")
    project_client = AIProjectClient(
        endpoint=os.getenv('PROJECT_ENDPOINT'),
        credential=DefaultAzureCredential()
    )
    console.print("✅ Client initialized successfully")
    
    # Create agent
    console.print("\n🎭 [bold]Creating agent...[/bold]")
    
    instructions = """
    You are Alex, a friendly and knowledgeable Azure AI assistant.
    
    Your mission is to help users learn Azure AI Foundry and agent development.
    
    Always:
    - Provide clear, helpful explanations
    - Use examples when possible
    - Be encouraging and supportive
    - Ask follow-up questions to better help
    
    Keep responses concise but informative.
    """
    
    agent = project_client.agents.create_agent(
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),
        name="Alex-Learning-Assistant",
        instructions=instructions.strip()
    )
    
    console.print(f"✅ Created agent: [cyan]{agent.name}[/cyan]")
    console.print(f"🆔 Agent ID: [dim]{agent.id}[/dim]")
    
    # Test conversation
    console.print("\n💬 [bold]Testing agent conversation...[/bold]")
    
    # Create thread
    thread = project_client.agents.threads.create()
    console.print(f"📞 Created thread: [dim]{thread.id}[/dim]")
    
    # Send message
    user_message = "Hello! I'm learning about Azure AI agents. Can you explain what makes them powerful?"
    
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    
    console.print(f"\n👤 [bold blue]User:[/bold blue] {user_message}")
    
    # Run agent
    run = project_client.agents.runs.create(
        thread_id=thread.id,
        agent_id=agent.id
    )
    
    # Wait for completion with progress
    console.print("⏳ Agent is thinking...")
    while run.status in ["queued", "in_progress"]:
        console.print(f"   Status: {run.status}")
        time.sleep(1)
        run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
    
    # Show response
    if run.status == "completed":
        messages = project_client.agents.messages.list(thread_id=thread.id)
        
        for msg in messages:
            if msg.role == "assistant":
                response = msg.content[0].text.value
                console.print(f"\n🤖 [bold green]Alex:[/bold green] {response}")
                break
    else:
        console.print(f"❌ Run failed: {run.status}")
    
    # Cleanup
    console.print(f"\n🧹 [bold]Cleaning up...[/bold]")
    project_client.agents.delete(agent.id)
    console.print("✅ Agent deleted")
    
    console.print(Panel.fit(
        "🎉 Congratulations! You've successfully created and tested your first Azure AI agent.\n\n"
        "Next: Learn about threads and runs in more detail.",
        style="bold green",
        title="✅ SUCCESS"
    ))

if __name__ == "__main__":
    try:
        create_and_test_agent()
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        console.print("\n💡 [bold]Troubleshooting tips:[/bold]")
        console.print("1. Run exercise_1_setup.py to validate your environment")
        console.print("2. Check your .env file has all required variables")
        console.print("3. Ensure you're authenticated with 'az login'")
```

So far, we have sent a message to the LLM and received a response. This is a good start, but it's not a conversation. In a real-world scenario, you would want to have a back-and-forth conversation with the agent. This is where threads come in.

### Threads

Threads are conversation sessions between an agent and a user. They store messages and automatically handle truncation to fit content into a model’s context. When you create a thread, you can append new messages to it as users respond. This allows you to maintain a persistent conversation with the agent, and the agent can refer back to previous messages in the conversation to provide more contextually relevant responses.

In the next section, we will learn how to create and manage threads to have a more natural conversation with our agent.

### Agent Reuse Patterns

One important pattern when working with agents is to avoid creating duplicate agents. In production scenarios, you should check if an agent already exists before creating a new one:

```python
def get_or_create_agent(project_client, agent_name, instructions, model):
    """Get an agent by name or create it if it doesn't exist."""
    
    # List all agents in the project
    agents_list = project_client.agents.list_agents()
    
    # Check if an agent with the given name already exists
    for agent in agents_list:
        if agent.name == agent_name:
            console.print(f"🤖 Found existing agent: [bold]'{agent.name}'[/bold] (ID: {agent.id})")
            return agent
            
    # If no agent is found, create a new one
    console.print(f"🤔 Agent '{agent_name}' not found, creating a new one...")
    agent = project_client.agents.create(
        name=agent_name,
        model=model,
        instructions=instructions
    )
    console.print(f"✅ Created new agent '[bold]{agent_name}[/bold]' with ID: [dim]{agent.id}[/dim]")
    return agent
```

This pattern is especially important for long-running applications or when running scripts multiple times, as it prevents the accumulation of duplicate agents in your project.

## 🎯 Exercises

### Exercise A: Create a Specialized Agent

Create an agent with a specific role. Try one of these:

1. **Code Review Assistant**: An agent that helps review Python code
2. **Learning Tutor**: An agent that explains complex topics step-by-step
3. **Creative Writer**: An agent that helps with creative writing tasks

### Exercise B: Agent Comparison

Create two agents with different personalities and have them "discuss" the same topic by:
1. Creating two agents with different instructions
2. Creating separate threads for each
3. Sending the same question to both
4. Comparing their responses

### Exercise C: Error Handling

Modify the basic example to include proper error handling for:
- Client initialization failures
- Agent creation errors
- Run timeout scenarios
- Message parsing issues

## 🔍 Best Practices

### Agent Instructions

1. **Be Specific**: Clear instructions lead to consistent behavior
2. **Define Role**: Explicitly state what the agent is and does
3. **Set Boundaries**: Specify what the agent should and shouldn't do
4. **Include Examples**: Show desired behavior patterns
5. **Consider Tone**: Define the communication style

### Resource Management

1. **Clean Up**: Always delete test agents to avoid resource limits using `project_client.agents.delete(agent.id)`
2. **Agent Reuse**: Use the `get_or_create_agent` pattern to avoid duplicate agents
3. **Handle Errors**: Wrap agent operations in try-catch blocks
4. **Monitor Costs**: Be aware of token usage in conversations
5. **Use Timeouts**: Don't wait indefinitely for runs to complete

### Security Considerations

1. **Validate Inputs**: Sanitize user messages
2. **Limit Scope**: Don't give agents more permissions than needed
3. **Monitor Usage**: Track agent interactions for security
4. **Protect Secrets**: Never include sensitive data in instructions

## 🔧 Troubleshooting

### Common Issues

**Agent creation fails with authentication error:**
- Verify `az login` is successful
- Check PROJECT_ENDPOINT format
- Ensure you have "Azure AI User" role

**Run hangs in "queued" status:**
- Check model deployment availability
- Verify quota limits
- Try with a different model

**Empty or malformed responses:**
- Review agent instructions for clarity
- Check if model supports your request type
- Verify message format

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **Agent Structure**: How agents are composed of instructions, models, and tools
2. **Client Usage**: How to use AIProjectClient for agent operations
3. **Basic Workflow**: Create agent → Create thread → Send message → Run agent → Get response
4. **Best Practices**: Resource management, error handling, and security considerations

## ➡️ Next Step

Now that you can create basic agents, learn about [Understanding Threads and Runs](./03-threads-runs.md) to master the conversation flow.

---

**Ready to code?** Run the exercise: `python exercises/exercise_2_basic_agent.py`
