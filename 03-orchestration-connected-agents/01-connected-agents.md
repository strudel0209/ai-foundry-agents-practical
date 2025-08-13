# Connected Agents in Azure AI Foundry (2025)

Connected agents let a primary agent invoke other specialized agents as tools during a run. This enables multi-agent orchestration with native tool-calling—no custom router code required.

Key concepts
- Primary agent: Receives the user prompt and decides when to call tools.
- Connected agents: Task-specific agents exposed as tools to the primary agent.
- Tool-calling: The primary agent uses model-native tool calls to invoke connected agents and incorporate their results.

How it works in this repo
- File: exercise_1_connected_agents.py
  - Creates three specialists (priority_agent, team_agent, effort_agent) using AgentsClient.create_agent.
  - Wraps each specialist as a ConnectedAgentTool. The SDK exposes their tool definitions (tool.definitions[0]).
  - Creates a primary triage agent with the connected agents’ tool definitions in its tools list.
  - Starts a thread, posts a user message, and runs create_and_process. The primary agent then calls the connected agents as needed and synthesizes the final reply.

Why this is idiomatic
- Uses out-of-box Azure AI Agents SDK types:
  - AgentsClient
  - ConnectedAgentTool
  - MessageRole, ToolSet (as needed), ListSortOrder
- Leverages the agent service’s built-in tool execution and result aggregation.
- No custom middleware/orchestrator is required—the service handles planning and tool invocation.

Minimal flow illustrated

1) Create specialists
- Priority agent: decides urgency.
- Team agent: chooses owning team.
- Effort agent: estimates effort.

2) Expose as tools
- For each agent, create ConnectedAgentTool(id=<agent.id>, name, description).
- Use tool.definitions[0] when assigning tools to the primary agent.

3) Create primary agent
- Instructions direct it to use connected tools to triage a ticket.
- Provide tools=[priority_tool.definitions[0], team_tool.definitions[0], effort_tool.definitions[0]].

4) Run
- Create a thread.
- Post a user message (the ticket).
- runs.create_and_process(thread_id, agent_id) executes the plan:
  - Primary agent decides which tools to call.
  - Connected agents run and return results.
  - Primary composes the final reply in the thread.

Prerequisites
- Environment:
  - PROJECT_ENDPOINT: Azure AI Foundry project endpoint (or AZURE_AI_PROJECT_ENDPOINT).
  - MODEL_DEPLOYMENT_NAME: Deployed model name (for example, gpt-4o-mini or equivalent).
- Auth:
  - DefaultAzureCredential in local dev typically requires `az login` in the dev container.
- Regions/quotas: Ensure the model and Agent Service are available in your region.

Run
- From this folder:
  - python3 exercise_1_connected_agents.py
- The script prints the final triage response and intermediate messages.

Tracing (optional)
- To see traces in Azure AI Foundry:
  - Attach an Application Insights resource to your Foundry project (Portal > Tracing).
  - In your app, configure Azure Monitor OpenTelemetry once (see the advanced orchestration example):
    - Set APPLICATIONINSIGHTS_CONNECTION_STRING, or
    - Set AZURE_AI_PROJECT_ENDPOINT/PROJECT_ENDPOINT so the SDK can fetch the connection string.
- After runs, open the project’s Tracing view to inspect spans.

Cleanup
- The sample includes commented-out deletion calls for the created agents.
- Un-comment them to keep your project tidy if you rerun the sample often.

Common pitfalls
- tools must use tool.definitions[0] from each ConnectedAgentTool when assigned to the primary agent.
- Use create_and_process to block until the run completes.
- Ensure MODEL_DEPLOYMENT_NAME matches a valid, deployed model in your project.
