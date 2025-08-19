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

The provided exercise demonstrates three key aspects of conversation management using Azure AI Foundry agents:

### 1. Single Thread Conversation (Demo 1)

- **Purpose:** Shows how a single thread maintains conversation context across multiple messages.
- **Implementation:** 
  - Creates one thread that persists throughout the conversation
  - Sends a series of related messages that build on each other
  - Agent remembers user's name (Alice) and preferences (hiking)
  - Demonstrates context retention within a single conversation session

### 2. Thread Isolation (Demo 2)

- **Purpose:** Demonstrates that different threads maintain completely separate contexts.
- **Implementation:**
  - Creates two separate threads with different "users" (Bob and Carol)
  - Each thread has its own conversation history
  - When asked "What do you remember about me?", each thread gives different answers
  - Shows that threads are isolated conversation containers

### 3. Thread Persistence (Demo 3)

- **Purpose:** Shows how threads can be resumed using their IDs.
- **Implementation:**
  - Reuses the thread from Demo 1
  - Simulates a user returning to a previous conversation
  - Agent recalls the entire conversation history
  - Demonstrates that threads persist and can be accessed later

### Key Components Explained:

#### ConversationDemo Class
- Manages the Azure AI client connection
- Creates and manages agents with specific instructions for demonstrating memory
- Provides helper methods for sending messages and extracting responses

#### Message Flow
1. **Create Thread:** Start a new conversation session
2. **Send Message:** Add user messages to the thread
3. **Create Run:** Process the thread to generate a response
4. **Monitor Status:** Wait for run completion
5. **Extract Response:** Retrieve the assistant's message

#### Helper Methods
- `_send_message_to_thread()`: Simplified method to send messages to any thread
- `_extract_message_content()`: Handles different message content structures
- `_show_thread_summary()`: Displays a table of conversation turns
- `_show_thread_history()`: Shows the complete conversation history

---

## 🔍 Azure AI Foundry Agent Features Demonstrated

### Thread Management
- **Thread Creation:** `project_client.agents.threads.create()`
- **Thread Persistence:** Threads remain accessible via their IDs
- **Thread Isolation:** Each thread maintains its own context

### Message Handling
- **Message Creation:** `project_client.agents.messages.create()`
- **Message Listing:** `project_client.agents.messages.list()`
- **Content Extraction:** Support for various message content formats

### Run Processing
- **Run Creation:** `project_client.agents.runs.create_and_process()`
- **Status Monitoring:** Automatic polling until completion
- **Error Handling:** Checks run status before retrieving responses

---

## 📊 Best Practices for Threads and Runs

### Thread Usage Patterns
- **One Thread Per Conversation:** Use a single thread for each user session
- **Thread Reuse:** Resume threads for returning users
- **Thread Isolation:** Create new threads for unrelated conversations

### Run Management
- **Status Checking:** Always verify run completion before reading responses
- **Error Handling:** Handle failed runs gracefully
- **Timeout Management:** Consider implementing timeouts for long-running operations

### Message Handling
- **Content Validation:** Check message content structure before accessing
- **Chronological Order:** Messages are returned in reverse chronological order
- **Role Filtering:** Filter messages by role (user/assistant) when needed

---

## 🎯 Key Takeaways

1. **Threads = Conversation Sessions:** Each thread represents a complete conversation with maintained context
2. **Messages = Individual Interactions:** User inputs and agent responses stored sequentially
3. **Runs = Processing Units:** Execute agent logic and generate responses
4. **Isolation = Privacy:** Threads don't share context, ensuring conversation privacy
5. **Persistence = Continuity:** Threads can be resumed anytime using their IDs

---

## 📖 Additional Resources

- [Threads, Runs, and Messages in Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/threads-runs-messages)
- [Agent Playground and Monitoring](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/vs-code-agents#explore-threads)
- [Quickstart: Create and Monitor Agents](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart#configure-and-run-an-agent)
- [2025 Azure AI Foundry SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)

---

## ➡️ Next Step

Once you've mastered threads and runs, proceed to [Tools](../02-tools/README.md) to learn about powering Azure AI Foundry agents with tools.
