# Module 4: Model Context Protocol (MCP) Integration

## Overview

This module demonstrates how to build, run, and integrate Model Context Protocol (MCP) servers with Azure AI Foundry agents. MCP is a standardized protocol for connecting AI agents to external tools and data sources, enabling real-time, secure, and extensible agent capabilities.

The folder `/04-mcp` contains everything you need to learn MCP fundamentals, set up a business-ready MCP server, and connect it to Azure AI Foundry agents using the latest SDKs and cloud deployment patterns.

---

## Folder Structure

- **01-mcp-server.md**  
  *Theory and hands-on for MCP server fundamentals. Explains protocol, architecture, and basic server implementation.*

- **exercises/exercise_1_mocking_mcp_server.py**  
  *Python exercise: Build a minimal MCP server with basic tools and resources. Learn JSON-RPC handling and protocol compliance.*

- **02-mcp-agents.md**  
  *Deep dive into integrating MCP servers with Azure AI Foundry agents. Explains agent SDK usage, tool/resource registration, and runtime invocation.*

- **exercises/exercise_2_mcp_agents.py**  
  *Python exercise: Connect an Azure AI Foundry agent to a SQLite MCP server. Demonstrates agent creation, tool configuration, and business analytics scenarios.*

- **scripts/**  
  *Contains everything for running a SQLite MCP server locally or in the cloud:*
  - `setup_sqlite_mcp_server.py`: Minimal HTTP MCP server for SQLite, streamable and cloud-ready.
  - `create_business_database.py`: Script to create a sample business database for MCP testing.
  - `requirements-mcp.txt`: Python requirements for MCP server and dependencies.
  - `Dockerfile`: Containerize the MCP server for Azure deployment.
  - `deploy-mcp-to-container-apps.sh`: Automated script to deploy MCP server to Azure Container Apps.
  - `README_SQLITE_MCP.md`: Step-by-step guide for MCP server setup, inspector usage, and integration tips.
  - `mcp-config/metadata.json`: Metadata for the business database.

---

## Getting Started

### 1. Learn MCP Protocol Fundamentals

- Read `01-mcp-server.md` for protocol concepts, architecture, and best practices.
- Run `exercises/exercise_1_mocking_mcp_server.py` to build and test a basic MCP server.

### 2. Set Up the SQLite MCP Server

- Follow `README_SQLITE_MCP.md` for quick setup instructions.
- Use `setup_sqlite_mcp_server.py` to launch a streamable HTTP MCP server with your business database.
- Optionally, use MCP Inspector for graphical testing and protocol debugging.

### 3. Deploy MCP Server to Azure

- Use the provided `Dockerfile` to containerize the MCP server.
- Run `deploy-mcp-to-container-apps.sh` to deploy to Azure Container Apps.
- Update your `.env` file with the public MCP server URL for agent integration.

### 4. Integrate with Azure AI Foundry Agents

- Read `02-mcp-agents.md` for a step-by-step guide to agent integration.
- Use `exercises/exercise_2_mcp_agents.py` to connect your agent to the MCP server and run business analytics scenarios.
- Experiment with different agent instructions, tool configurations, and business queries.

---

## Key Concepts

- **MCP Server**: Exposes tools and resources via JSON-RPC over HTTP. Implements methods like `tools/list`, `tools/call`, `resources/list`, and `resources/read`.
- **Agent SDK**: Azure AI Foundry Python SDK lets you define agents, register MCP tools, and orchestrate runs and threads.
- **Tool Registration**: Agents reference MCP servers via `server_url` and `server_label`. Allowed tools can be restricted for security.
- **Tool Invocation**: At runtime, agents call MCP tools using the `tool_resources` parameter, controlling approval workflows as needed.

---

## Best Practices

- **Public Endpoint**: MCP servers must be accessible from Azure (not `localhost`). Use Azure Container Apps, ngrok, or similar tunneling for development.
- **CORS**: Ensure your MCP server sets appropriate CORS headers for browser and cloud access.
- **Protocol Compliance**: Implement all required MCP methods and return valid JSON-RPC responses.
- **Security**: Only expose necessary tools and resources; use approval workflows for sensitive operations if needed.
- **Debugging**: Use `/health` and `/capabilities` endpoints to verify MCP server status and tool discovery.

---

## References & Further Reading

- [Azure AI Foundry: Model Context Protocol Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/introduction)
- [azure-ai-foundry/mcp-foundry (GitHub)](https://github.com/azure-ai-foundry/mcp-foundry)
- [AI-Gateway: Azure API Management + MCP + Foundry](https://github.com/Azure-Samples/AI-Gateway)
- [devkimchi/meai-azure-ai-foundry-mcp-sample (GitHub)](https://github.com/devkimchi/meai-azure-ai-foundry-mcp-sample)

---

## Next Steps

1. Experiment with MCP Inspector and the SQLite MCP server.
2. Deploy your MCP server to Azure and update your agent configuration.
3. Build custom tools and resources for your business scenarios.
4. Explore advanced agent orchestration and multi-server integration.

With this folder, you have everything needed to master MCP server development and agent integration for real-world business intelligence and AI workflows.
