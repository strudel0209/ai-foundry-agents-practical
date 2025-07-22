# 3. Understanding Threads and Runs

In this lesson, you'll master the conversation flow in Azure AI Foundry agents through threads and runs—the core execution model that powers agent interactions.

## 🎯 Objectives

- Understand the thread and run execution model
- Create and manage conversation threads
- Monitor run states and handle different scenarios
- Implement proper polling and status handling
- Build conversation history management
- Handle tool execution during runs

---

## 🧠 Key Concepts

### What Are Threads and Runs?

**Threads** in Azure AI Foundry agents represent persistent conversation sessions between a user and an agent. Each thread maintains the full context of the conversation, storing all messages exchanged. This enables multi-turn, context-aware interactions, allowing the agent to reference previous messages and maintain continuity.

**Runs** are activations of an agent to process the messages in a thread. When a run is started, the agent uses its configuration and the thread's messages to perform tasks, call tools, and generate responses. Runs are tracked with detailed status updates and execution steps.

**Why Is This Important?**

- **Context Retention:** Threads ensure that the agent can maintain and reference conversation history, enabling more natural and intelligent responses.
- **Stateful Execution:** Runs allow you to monitor the agent's progress, handle tool calls, and manage asynchronous workflows.
- **Debugging & Monitoring:** By tracking run states and steps, you can diagnose issues, optimize performance, and ensure reliable agent behavior.

---

## 💡 How the Code Works

The provided exercise demonstrates advanced conversation management using Azure AI Foundry agents. Here's what it does:

### 1. ConversationManager Class

- **Purpose:** Manages multiple conversation threads, tracks history, and coordinates agent interactions.
- **Features:** 
  - Creates new threads for different scenarios.
  - Adds messages to threads, recording user and assistant exchanges.
  - Maintains a structured history for each conversation.

### 2. Creating and Managing Threads

- **Thread Creation:** Each scenario or user session starts with a new thread, ensuring isolated context.
- **Message Addition:** User messages are appended to the thread, and the agent's responses are tracked.

### 3. Executing Runs and Monitoring Status

- **Run Execution:** For each user message, a run is started to process the thread and generate a response.
- **Status Polling:** The code continuously monitors the run status (`queued`, `in_progress`, `requires_action`, `completed`, etc.), providing live feedback.
- **Run Steps:** Detailed execution steps are retrieved, showing tool calls, message creation, and other agent actions.

### 4. Handling Tool Execution

- **Tool Calls:** If the agent needs to use a tool (e.g., calculator, time lookup), the code simulates tool execution and submits outputs back to the run.
- **Approval Workflow:** The code handles `requires_action` states, ensuring tool outputs are provided as needed.

### 5. Conversation History and Export

- **History Tracking:** All messages and responses are stored, allowing for review and export.
- **Export:** Conversations can be saved to JSON files for analysis or auditing.

### 6. Scenario Demonstrations

- **Multi-Turn Q&A:** Shows how the agent maintains context across multiple exchanges.
- **Tool Usage:** Demonstrates agent-initiated tool calls and result handling.
- **Context Retention:** Validates the agent's ability to remember and reference earlier information.

---

## 🔍 Azure AI Foundry Agent Features for Threads and Runs

- **Persistent Threads:** Maintain full conversation history for context-aware responses.
- **Flexible Message Handling:** Support for text, images, and files in messages.
- **Run Monitoring:** Track run status, execution steps, and tool calls for transparency and debugging.
- **Tool Integration:** Agents can invoke tools during runs, with support for approval workflows and output submission.
- **Conversation Isolation:** Each thread is independent, enabling multiple concurrent sessions.
- **Export & Audit:** Conversation data can be exported for compliance, analysis, or training.

---

## 📊 Why Monitoring Threads and Runs Matters

- **Reliability:** Ensures agents complete tasks and respond appropriately.
- **Debugging:** Identifies where runs fail or require intervention.
- **Performance:** Tracks execution times and tool usage for optimization.
- **Security & Compliance:** Maintains audit trails of all interactions.
- **User Experience:** Enables seamless, context-rich conversations.

---

## 📖 Additional Resources

- [Threads, Runs, and Messages in Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/threads-runs-messages)
- [Agent Playground and Monitoring](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/vs-code-agents#explore-threads)
- [Quickstart: Create and Monitor Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart#configure-and-run-an-agent)
- [2025 Azure AI Foundry SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)

---

## ➡️ Next Step

Once you've mastered threads and runs, proceed to [Tools](../02-tools/README.md) to learn about powering Azure AI Foundry agents with tools.
