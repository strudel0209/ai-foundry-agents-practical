# 1. MCP Server Fundamentals - Building Model Context Protocol Servers

In this lesson, you'll master the fundamentals of creating Model Context Protocol (MCP) servers that extend Azure AI agent capabilities with external tools and resources. MCP enables secure, standardized connections between agents and external data sources.

## 🎯 Objectives

- Understand MCP architecture and protocol design
- Build basic MCP servers with tools and resources
- Implement JSON-RPC 2.0 communication patterns
- Create server-side protocol handling
- Test MCP server functionality and integration

## 🧠 Key Concepts

### What is Model Context Protocol (MCP)?

Model Context Protocol (MCP) is an open protocol designed to standardize how AI models and agents interact with external tools, data sources, and services. Think of MCP as the "USB-C standard" for AI applications - it provides a universal way to connect AI systems to the world of data and capabilities they need.

#### Core MCP Principles

1. **Standardization**: MCP provides a consistent interface for AI-to-service communication, regardless of the underlying implementation
2. **Security**: Built-in authentication and authorization mechanisms ensure safe interactions
3. **Flexibility**: Supports both local and remote servers, enabling various deployment scenarios
4. **Extensibility**: Easy to add new tools, resources, and capabilities without changing the core protocol
5. **Stateful Context**: Maintains context across interactions for more intelligent conversations

### MCP Architecture Deep Dive

![MCP Architecture](/data/fig1-MCP_Architecture.png)

### MCP Communication Flow

![MCP Workflow](/data/fig2-MCP_Workflow.png)

### Key MCP Components Explained

#### 1. MCP Hosts
AI applications that need to access external capabilities. Examples include:
- **VS Code with GitHub Copilot**: Uses MCP to access project context
- **Azure AI Foundry**: Integrates MCP servers as agent tools
- **Claude Desktop**: Connects to MCP servers for enhanced capabilities
- **Custom AI Applications**: Any app using MCP clients

#### 2. MCP Clients
Protocol clients that maintain connections with servers:
- Handle JSON-RPC 2.0 message formatting
- Manage connection lifecycle
- Implement retry logic and error handling
- Cache server capabilities

#### 3. MCP Servers
Lightweight programs exposing specific capabilities:
- **Local Servers**: Run on the same machine, use stdio transport
- **Remote Servers**: Accessible over HTTP/SSE, support OAuth
- **Containerized Servers**: Deploy to Azure Container Apps or Kubernetes

#### 4. Tools
Executable functions that agents can invoke:
- Defined with JSON Schema for input validation
- Return structured responses
- Can be synchronous or asynchronous
- Support streaming for long-running operations

#### 5. Resources
Data sources that agents can read:
- Identified by unique URIs (e.g., `mcp://server/data`)
- Support different MIME types
- Can be static or dynamic
- Enable subscription for real-time updates

## 🚀 Building MCP Servers for Azure AI Foundry

### Latest Resources and Best Practices (2025)

#### Official MCP Resources

1. **[Model Context Protocol Specification](https://modelcontextprotocol.io/docs)**
   - Official protocol documentation
   - Reference implementations
   - SDK documentation for multiple languages

2. **[Azure MCP Server](https://github.com/Azure/azure-mcp)**
   - Official Azure implementation
   - Integrates with Azure services
   - Supports Entra ID authentication

3. **[MCP TypeScript/JavaScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)**
   - Most mature SDK
   - Extensive examples
   - Best for Node.js servers

4. **[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)**
   - Growing ecosystem
   - Good for data science integrations
   - Compatible with Azure Functions

5. **[MCP C# SDK](https://github.com/modelcontextprotocol/csharp-sdk)**
   - Microsoft partnership
   - Ideal for .NET developers
   - Integrates with Semantic Kernel

#### Azure-Specific MCP Implementations

1. **Azure Container Apps MCP Servers**
   - Deploy MCP servers as microservices
   - Auto-scaling and managed infrastructure
   - Built-in authentication with Managed Identity

2. **Azure Functions MCP Servers**
   - Serverless MCP implementation
   - Cost-effective for intermittent usage
   - Easy integration with Azure services

3. **Azure AI Foundry MCP Integration**
   - Native support for MCP tools in agents
   - Automatic discovery of MCP endpoints
   - Secure credential management

### Deployment Patterns for Production

#### 1. Local Development Pattern
```
Developer Machine
├── MCP Server (stdio)
├── AI Agent/Client
└── Local Resources
```
- Use for rapid prototyping
- No network overhead
- Ideal for development

#### 2. Containerized Pattern
```
Azure Container Apps
├── MCP Server Container
├── Load Balancer
├── Authentication Layer
└── Azure Services Integration
```
- Production-ready deployment
- Scalable and reliable
- Supports multiple clients

#### 3. Serverless Pattern
```
Azure Functions
├── HTTP Triggered Functions
├── MCP Protocol Handler
├── Azure Service Bindings
└── Managed Identity
```
- Cost-effective for light usage
- Automatic scaling
- Minimal maintenance

### Implementation Guide

For a complete implementation example, refer to `exercise_1_mocking_mcp_server.py` in the exercises folder. The script demonstrates:

1. **Basic MCP Server Structure**: Core server class with initialization
2. **Tool Registration**: How to define and register tools with schemas
3. **Resource Management**: Creating and serving resources
4. **Protocol Handling**: JSON-RPC 2.0 message processing
5. **Testing Framework**: Comprehensive test suite for validation

Key implementation aspects covered in the exercise:
- Message handling with proper JSON-RPC 2.0 compliance
- Tool execution with input validation
- Resource serving with MIME type support
- Error handling and logging
- Asynchronous operation support

## 🎯 Exercises

### Exercise A: Explore MCP Ecosystem

1. **Install MCP Inspector**
   - Use the MCP Inspector tool to explore server capabilities
   - Test against example MCP servers
   - Understand the protocol flow

2. **Try Different MCP Servers**
   - Test the Azure MCP Server
   - Explore community MCP servers
   - Compare different implementations

### Exercise B: Deploy to Azure

1. **Container Apps Deployment**
   - Package your MCP server as a container
   - Deploy to Azure Container Apps
   - Configure authentication

2. **Azure Functions Deployment**
   - Create a serverless MCP server
   - Implement basic tools
   - Test with Azure AI agents

### Exercise C: Advanced Integration

1. **Multi-Server Orchestration**
   - Connect multiple MCP servers
   - Implement server discovery
   - Create a server registry

2. **Custom Protocol Extensions**
   - Extend MCP with custom capabilities
   - Maintain backward compatibility
   - Document your extensions

## 🔍 Best Practices

### MCP Server Design

1. **Clear Tool Definitions**: Use comprehensive JSON schemas
2. **Idempotent Operations**: Ensure tools can be safely retried
3. **Resource Organization**: Use logical URI hierarchies
4. **Error Messages**: Provide actionable error information
5. **Performance**: Implement caching and connection pooling

### Security Considerations

1. **Authentication**: Always implement proper authentication
2. **Authorization**: Use role-based access control
3. **Input Validation**: Validate all inputs against schemas
4. **Rate Limiting**: Protect against abuse
5. **Audit Logging**: Track all operations

### Production Deployment

1. **Health Checks**: Implement comprehensive health endpoints
2. **Monitoring**: Use Azure Monitor and Application Insights
3. **Versioning**: Support multiple protocol versions
4. **Documentation**: Generate OpenAPI/AsyncAPI specs
5. **Testing**: Implement integration and load tests

## 🔧 Troubleshooting

### Common Issues

**Connection Problems:**
- Verify network connectivity and firewall rules
- Check authentication credentials
- Validate server URL and transport configuration
- Monitor connection timeout settings

**Protocol Errors:**
- Ensure JSON-RPC 2.0 compliance
- Validate message structure
- Check method names and parameters
- Review error response handling

**Performance Issues:**
- Profile server response times
- Implement connection pooling
- Add caching layers
- Optimize database queries

**Integration Challenges:**
- Test with MCP Inspector first
- Verify capability negotiation
- Check tool and resource schemas
- Monitor server logs

## 📖 Key Takeaways

After completing this lesson, you should understand:

1. **MCP Architecture**: The complete ecosystem from hosts to resources
2. **Protocol Details**: JSON-RPC 2.0 communication patterns
3. **Server Types**: Local vs. remote deployment options
4. **Azure Integration**: How to deploy MCP servers on Azure
5. **Best Practices**: Security, performance, and reliability considerations

## ➡️ Next Step

Once you've mastered basic MCP server concepts, proceed to [Business MCP Integration](./02-business-mcp.md) to learn enterprise-grade MCP server patterns.

---

**💡 Pro Tip**: Start with local MCP servers for development, then progress to containerized deployments for production. The Azure MCP Server provides an excellent reference implementation for building production-ready servers.
