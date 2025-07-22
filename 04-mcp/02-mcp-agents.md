# Integrating MCP Servers with Azure AI Foundry Agents SDK

This guide explains how to connect streamable HTTP Model Context Protocol (MCP) server to Azure AI Foundry agents using the Python SDK.
---

## What is MCP and Why Use It?

Model Context Protocol (MCP) is an open standard for exposing tools and contextual data to AI agents and LLMs. MCP servers provide a uniform interface for tool discovery, invocation, and resource inspection, enabling agents to interact with external systems (databases, APIs, business logic) in a scalable, secure, and model-agnostic way.

Azure AI Foundry Agent Service natively supports MCP tools, allowing you to extend agent capabilities with any MCP-compliant server—whether hosted on Azure, locally, or by a third party.

---

## Key Concepts

- **MCP Server**: A service exposing tools and resources via MCP methods (`tools/list`, `tools/call`, `resources/list`, etc.) over HTTP (streamable or standard).
- **Agent SDK**: Azure AI Foundry Python SDK lets you define agents, configure tools, and orchestrate runs and threads.
- **Tool Registration**: Agents reference MCP servers via a `server_url` and a unique `server_label`. Allowed tools can be restricted for security or simplicity.
- **Tool Invocation**: At runtime, agents call MCP tools using the `tool_resources` parameter, optionally controlling approval workflows.

---

## Visualizing and Testing MCP Servers with MCP Inspector

Before connecting your MCP server to Azure AI Foundry agents, it's best practice to visually inspect and test your MCP server using the **MCP Inspector**. [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector) is a visual and CLI tool for debugging, validating, and interacting with MCP servers in real time.

### Why Use MCP Inspector?

- **Visualize available tools and resources** exposed by your MCP server
- **Interactively test tool calls and responses** before agent integration
- **Debug and validate MCP protocol compliance**
- **Export server launch configurations** for use in IDEs and agent frameworks

### Step-by-Step Guide: Visualizing Your MCP Server with MCP Inspector

1. **Install MCP Inspector (if not already available)**
   ```bash
   # Run MCP Inspector directly with npx (no install needed)
   npx @modelcontextprotocol/inspector
   ```
   Or, for local development:
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Start your MCP server**
   ```bash
   python ./scripts/setup_sqlite_mcp_server.py
   ```
   Or use any MCP-compliant server endpoint.

3. **Launch MCP Inspector and connect to your MCP server**
   ```bash
   # Start MCP Inspector and provide your MCP server URL
   npx @modelcontextprotocol/inspector --server http://localhost:3000
   ```
   - The Inspector UI will open in your browser.
   - You can also use the CLI for advanced testing.

4. **Explore Tools and Resources**
   - The Inspector will list all available tools (`tools/list`) and resources (`resources/list`) exposed by your MCP server.
   - Click on any tool to view its schema, parameters, and try out sample invocations.

5. **Test Tool Calls**
   - Use the Inspector's UI to send requests to your MCP server.
   - View real-time responses, debug errors, and validate output formats.

6. **Export Configuration for IDEs**
   - MCP Inspector provides convenient buttons to export server launch configurations (e.g., for Visual Studio Code, Cursor, Claude Code).
   - The configuration file is usually called `mcp.json`.

7. **Advanced Features**
   - Inspect prompt templates, tool schemas, and resource metadata.
   - Use the Inspector to simulate agent workflows and verify protocol compliance.

**References:**
- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [MCP Inspector Guide (2025)](https://www.mcpevals.io/blog/mcp-inspector-guide)
- [Visual Studio Marketplace: MCP Inspector Extension](https://marketplace.visualstudio.com/items?itemName=DhananjaySenday.mcp--inspector)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/introduction)

---

## Setting up the SQLite MCP Server

The `scripts` folder contains everything you need to set up a complete SQLite MCP server for business analytics. Azure AI Foundry agents **only support HTTP streamable MCP servers**, not local stdio-based servers.

### Option 1: Deploy to Azure Container Apps (Recommended)

For production use and Azure AI Foundry integration, deploy the MCP server to Azure Container Apps:

1. **Make the deployment script executable**:
   ```bash
   chmod +x ./scripts/deploy-mcp-to-container-apps.sh
   ```

2. **Deploy the MCP server to Azure**:
   ```bash
   ./scripts/deploy-mcp-to-container-apps.sh
   ```

3. **Update your .env file** with the provided public URL:
   ```
   MCP_SERVER_URL=https://your-container-app-url.azurecontainerapps.io
   ```

### Option 2: Local Development with Tunneling

For testing and development:

1. **Create the business database**:
   ```bash
   python ./scripts/create_business_database.py
   ```

2. **Start the local MCP server**:
   ```bash
   python ./scripts/setup_sqlite_mcp_server.py
   ```

3. **Expose your localhost** with ngrok:
   ```bash
   # Install ngrok if needed
   npm install -g ngrok
   
   # Create a tunnel
   ngrok http 3000
   ```

4. **Update your .env file** with the ngrok URL:
   ```
   MCP_SERVER_URL=https://your-random-subdomain.ngrok.io
   ```

### Option 3: Testing with MCP Inspector

To visually test your MCP server before connecting to Azure AI Foundry:

```bash
# Start server with Inspector
python ./scripts/setup_sqlite_mcp_server.py --inspector
```

The MCP Inspector will open in your browser, allowing you to test SQL queries interactively:

```sql
-- List all tables
SELECT name FROM sqlite_master WHERE type='table';

-- View customers
SELECT * FROM customers;

-- Financial analysis
SELECT year, quarter, revenue, expenses, profit FROM financials ORDER BY year DESC, quarter DESC;
```

## Understanding the SQLite MCP Server

The SQLite MCP server (`setup_sqlite_mcp_server.py`) exposes these business tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `sql_query` | Execute SQL queries on the database | `query` (required), `params` (optional) |
| `list_tables` | List all tables in the database | None |
| `table_schema` | Get schema for a specific table | `table` (required) |

The business database contains the following tables:
- `customers`: Customer information and demographics
- `orders`: Order details and transaction data
- `products`: Product catalog and inventory
- `sales`: Sales data and trends
- `employees`: Employee performance metrics
- `financials`: Financial data by quarter (revenue, expenses, profit)

## Connecting Azure AI Foundry Agents to the MCP Server

### 1. Environment Setup

Ensure your `.env` file contains:

```env
MCP_SERVER_URL=https://your-mcp-server-url
```

### 2. Agent Configuration

- Use the Azure AI Foundry SDK to create an agent.
- In the agent's `tools` list, add an MCP tool with:
  - `type`: `"mcp"`
  - `server_label`: a unique identifier (letters, numbers, underscores only)
  - `server_url`: the MCP server's public HTTP endpoint
  - `allowed_tools`: list of tool names the agent can use

**Example (conceptual):**
```python
tools=[
    {
        "type": "mcp",
        "server_label": "sqlite_business",
        "server_url": "https://your-mcp-server-url",
        "allowed_tools": ["sql_query", "list_tables", "table_schema"]
    }
]
```

### 3. Thread and Message Creation

- Create a thread for each user-agent interaction.
- Add user messages to the thread, describing the business scenario or query.

### 4. Running the Agent with MCP Tool Resources

- When starting a run, pass `tool_resources` as a dictionary:
  - `"mcp"`: a list of objects, each with `server_label` matching the agent tool, and optional approval settings.
  - For most use cases, `"require_approval": "never"` disables manual approval for tool calls.

**Minimal example:**
```python
tool_resources={
    "mcp": [
        {
            "server_label": "sqlite_business",
            "require_approval": "never"
        }
    ]
}
```

### 5. Polling and Handling Results

- Poll the run status until completion.
- If the run status is `"requires_action"`, handle approval as needed (usually not required for `"never"`).
- On completion, retrieve and display the agent's response from the thread messages.

---

## Best Practices

- **Public Endpoint**: MCP servers must be accessible from Azure (not `localhost`). Use Azure Container Apps, ngrok, or similar tunneling for development.
- **CORS**: Ensure your MCP server sets appropriate CORS headers for browser and cloud access.
- **Protocol Compliance**: Implement all required MCP methods and return valid JSON-RPC responses.
- **Security**: Only expose necessary tools and resources; use approval workflows for sensitive operations if needed.
- **Debugging**: Use `/health` and `/capabilities` endpoints to verify MCP server status and tool discovery.

---

## Advanced Scenarios

- **Multiple MCP Servers**: Register multiple MCP tools with different `server_label` and `server_url` values.
- **Custom Headers**: Pass authentication or session headers in `tool_resources` if your MCP server requires them.
- **Resource Discovery**: Use `resources/list` and `resources/read` to let agents inspect and query external data sources.

---

## References & Further Reading

- [Azure AI Foundry: Model Context Protocol Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/introduction)
- [azure-ai-foundry/mcp-foundry (GitHub)](https://github.com/azure-ai-foundry/mcp-foundry)
- [devkimchi/meai-azure-ai-foundry-mcp-sample (GitHub)](https://github.com/devkimchi/meai-azure-ai-foundry-mcp-sample)
- [Azure AI Foundry Python SDK Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart)

---

## Getting Started

1. Deploy or run a streamable HTTP MCP server.
2. Register the MCP server as a tool in your Azure AI Foundry agent.
3. Use the SDK to create threads, send messages, and run the agent with MCP tool resources.
4. Retrieve and use the agent's output for your business scenario.

With this setup, you can connect any MCP-compliant server to Azure AI Foundry agents and unlock powerful, real-time integrations with external data and tools.
