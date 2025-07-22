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

Once you've mastered threads and runs, proceed to [Tools](02-tools) to learn about powering Azure AI Foundry agents with tools
