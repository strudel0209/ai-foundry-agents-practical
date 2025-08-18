# Connected agents in Azure AI Foundry

Connected agents let a primary agent call other specialized agents as tools during a run. This enables multi-agent orchestration using native tool-calling—no custom router or middleware required.

> TL;DR: Create specialist agents, expose each as a ConnectedAgentTool, give their tool definitions to a primary agent, then run a thread. The primary will call the specialists as needed and synthesize the final reply.

## Key terms

- Primary agent: Receives the user prompt and decides when to call tools.
- Connected agents: Task-specific agents exposed as tools to the primary agent.
- Tool-calling: The primary uses model-native tool calls to invoke connected agents and incorporate their results.

## Where this lives in the repo

- File: `exercise_1_connected_agents.py`
  - Creates three specialists (`priority_agent`, `team_agent`, `effort_agent`) with `AgentsClient.create_agent`.
  - Wraps each specialist as a `ConnectedAgentTool` and uses its tool definition (`tool.definitions[0]`).
  - Creates a primary triage agent with those tool definitions in its `tools` list.
  - Starts a thread, posts a user message, and calls `runs.create_and_process`. The primary invokes connected agents and composes the final triage reply.

## Why this is idiomatic

- Uses out-of-the-box Azure AI Agents SDK types:
  - `AgentsClient`
  - `ConnectedAgentTool`
  - `MessageRole`, `ToolSet` (as needed), `ListSortOrder`
- Leverages the service’s built-in planning, tool execution, and result aggregation.
- Avoids custom orchestrators—simpler, more reliable, and traceable.

## End-to-end flow

1) Create specialists
   - Priority agent: determines urgency.
   - Team agent: selects the owning team.
   - Effort agent: estimates work effort.

2) Expose as tools
   - For each agent, create `ConnectedAgentTool(id=<agent.id>, name, description)`.
   - Use `tool.definitions[0]` when assigning tools to the primary.

3) Create the primary agent
   - Instructions: “Use the connected tools to triage a ticket.”
   - Provide `tools=[priority_tool.definitions[0], team_tool.definitions[0], effort_tool.definitions[0]]`.

4) Run
   - Create a thread and post the ticket as a user message.
   - Call `runs.create_and_process(thread_id, agent_id)` to block until completion:
     - The primary decides which tools to call and in what order.
     - Connected agents execute and return results.
     - The primary writes the final reply to the thread.

## Prerequisites

- Environment variables
  - `PROJECT_ENDPOINT` or `AZURE_AI_PROJECT_ENDPOINT`: Foundry project endpoint URL.
  - `MODEL_DEPLOYMENT_NAME`: Deployed model name (e.g., `gpt-4o-mini` or equivalent in your region).
- Authentication
  - Local dev uses `DefaultAzureCredential`; run `az login` in the dev container before executing.
- Capacity/region
  - Ensure the model deployment and the Agents service are available and quota is sufficient in your region.

## Quickstart

From this folder:

```bash
python3 exercise_1_connected_agents.py
```

The script prints intermediate messages and the final triage response.

## Tracing (optional)

To see traces in Azure AI Foundry:

1) Attach an Application Insights resource to your Foundry project (Portal → Tracing).
2) Configure Azure Monitor OpenTelemetry in your app once (see the advanced orchestration example):
   - Set `APPLICATIONINSIGHTS_CONNECTION_STRING`, or
   - Set `AZURE_AI_PROJECT_ENDPOINT`/`PROJECT_ENDPOINT` so the SDK can fetch the connection string.
3) After runs, open the project’s Tracing view to inspect spans.

## Cleanup

The sample includes commented-out deletion calls for the created agents. Un-comment them to keep your project tidy if you rerun the sample often.

## Common pitfalls and fixes

- Using the wrong tool object: Assign `tool.definitions[0]` from each `ConnectedAgentTool` to the primary agent’s `tools` list.
- Asynchronous confusion: Use `create_and_process` to block until the run completes and tool calls finish.
- Deployment name mismatch: Ensure `MODEL_DEPLOYMENT_NAME` points to a valid, deployed model in your Foundry project and region.

