# 2. Creating Your First Agent

In this lesson, you'll learn how to create your first Azure AI Foundry agent using the provided exercise script. We'll walk through the workflow, explain the key concepts, and show you how to run and test your agent.

## 🎯 Objectives

- Understand Azure AI agent architecture and workflow
- Create your first agent with custom instructions
- Initiate a conversation and interact with the agent
- Learn about threads, runs, and model selection
- Test basic agent functionality and review responses

---

## 🚀 How to Run the Exercise

All code for this lesson is in `exercises/exercise_2_basic_agent.py`.

**Step 1: Validate your environment**

Before running the agent, ensure your environment is set up and validated:

```bash
python exercises/exercise_1_setup.py
```

**Step 2: Run the agent creation and conversation script**

```bash
python exercises/exercise_2_basic_agent.py
```

---

## 🧠 What Does the Script Do?

### 1. Loads Environment Variables

The script uses `.env` for configuration, including:
- `PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT_NAME`: The model deployment name (e.g., `gpt-4o-mini`)

### 2. Initializes the Azure AI Project Client

Uses the SDK to connect to your Azure AI Foundry project:

```python
project_client = AIProjectClient(
    endpoint=os.getenv('PROJECT_ENDPOINT'),
    credential=DefaultAzureCredential()
)
```

### 3. Creates an Agent with Custom Instructions

Defines a friendly, knowledgeable agent ("Learning-Assistant") with detailed instructions and personality traits. Instructions guide the agent's behavior, tone, and expertise.

**Model Selection:**  
The agent uses the model specified in your environment (`MODEL_DEPLOYMENT_NAME`). For general tasks and learning scenarios, `gpt-4o-mini` is recommended. For code or data tasks, choose a model with relevant capabilities.

### 4. Displays Agent Properties

Shows agent details such as name, ID, model, and instructions preview for transparency and debugging.

### 5. Initiates a Conversation (Thread)

Creates a new thread, which represents a conversation session. Threads maintain context and allow multi-turn interactions.

### 6. Sends User Messages

Sends a series of test questions to the agent, simulating a real user conversation.

### 7. Runs the Agent and Polls for Completion

Starts a run for each message, activating the agent to process the thread and respond. The script polls the run status until completion.

### 8. Retrieves and Displays Responses

After each run, the script fetches the assistant's response from the thread and displays it.

### 9. Cleans Up Resources

Deletes the agent after the test to avoid resource accumulation.

---

## 💬 Conversation Flow

The script demonstrates the following workflow:

1. **Create Agent** → 2. **Create Thread** → 3. **Send Message** → 4. **Run Agent** → 5. **Get Response**

This mirrors the recommended Azure AI Foundry agent execution model:
- **Agent**: Custom AI with instructions and model
- **Thread**: Conversation context
- **Message**: User or assistant communication
- **Run**: Agent activation to process messages

---

## 📝 Step-by-Step Breakdown

1. **Agent Creation**:  
   - Uses your chosen model (e.g., `gpt-4o-mini`)
   - Instructions define agent's role and style

2. **Thread Management**:  
   - Each conversation uses a new thread for context retention

3. **Message Handling**:  
   - User messages are sent to the thread
   - Agent responds based on instructions and context

4. **Run States**:  
   - `queued` → `in_progress` → `completed` (or error states)
   - Script polls until run is finished

5. **Response Retrieval**:  
   - Assistant's reply is fetched and displayed

6. **Cleanup**:  
   - Agent is deleted after the test

---

## 🔍 Best Practices

- **Use clear, detailed instructions** for consistent agent behavior
- **Choose the right model** for your use case (see [Azure AI Foundry Models](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart))
- **Reuse agents** when possible to avoid duplicates
- **Clean up resources** to stay within quotas
- **Monitor run states** and handle errors gracefully

---

## 📖 Additional Resources

- [Azure AI Foundry Agents Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart)
- [SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Agent Playground](https://ai.azure.com)
- [Latest Model Info](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/models)


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

