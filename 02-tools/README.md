# Module 2: Tools - Advanced Agent Capabilities

This module explores the powerful tools available to Azure AI Foundry agents, enabling them to perform complex tasks beyond simple text generation. Each tool expands your agent's capabilities in specific ways, from searching through documents to executing custom business logic.

## 🎯 Module Overview

Azure AI Foundry agents can be equipped with three fundamental tool types:

1. **[File Search](01-file-search.md)** - Retrieval Augmented Generation (RAG) capabilities
2. **[Code Interpreter](02-code-interpreter.md)** - Python code execution and data analysis
3. **[Function Calling](03-function-calling.md)** - Custom business logic integration

## 📚 Learning Path

### Prerequisites

- Completion of [Module 1: Fundamentals](../01-fundamentals/README.md)
- Basic understanding of Python and REST APIs
- Familiarity with file formats (PDF, CSV, JSON, etc.)

### Time Investment

- **Total Time**: 4-5 hours
- **File Search**: 90 minutes
- **Code Interpreter**: 90 minutes  
- **Function Calling**: 75 minutes
- **Integration Practice**: 60 minutes

## 🔧 Tool Capabilities Matrix

| Tool | Data Processing | External Integration | Real-time Execution | Use Cases |
|------|----------------|---------------------|-------------------|-----------|
| **File Search** | ✅ Documents, PDFs, Text | ❌ Read-only | ❌ Pre-indexed | Knowledge bases, Documentation, Research |
| **Code Interpreter** | ✅ Data analysis, Visualization | ❌ Sandboxed environment | ✅ Dynamic execution | Data science, Charts, Calculations |
| **Function Calling** | ✅ Custom logic | ✅ APIs, Databases, Services | ✅ Real-time integration | Business logic, Validations, Workflows |

## 🚀 Quick Start

Each tool lesson follows this structure:

1. **Concepts & Architecture** - Understanding the tool's capabilities
2. **Implementation** - Step-by-step code examples
3. **Best Practices** - Enterprise-grade patterns
4. **Exercises** - Hands-on practice scenarios
5. **Troubleshooting** - Common issues and solutions

### Basic Tool Integration Pattern

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FileSearchTool, CodeInterpreterTool, FunctionTool

# Create client
client = AIProjectClient(
    endpoint=os.getenv('PROJECT_ENDPOINT'),
    credential=DefaultAzureCredential()
)

# Configure tools
file_search = FileSearchTool()
code_interpreter = CodeInterpreterTool()
function_tool = FunctionTool(functions={custom_function})

# Create agent with multiple tools
agent = client.agents.create_agent(
    model=os.getenv('MODEL_DEPLOYMENT_NAME'),
    name="multi-tool-agent",
    instructions="You are a comprehensive business assistant with access to multiple tools.",
    tools=[file_search, code_interpreter, function_tool.definitions]
)
```

## 📖 Detailed Lessons

### 1. File Search - Retrieval Augmented Generation

**[📄 Complete Guide](01-file-search.md)** | **[💻 Exercise](exercises/exercise_1_file_search.py)**

Transform your agents into knowledge experts by connecting them to document repositories. Learn to:

- Upload and index documents for search
- Implement RAG patterns for accurate information retrieval
- Handle multiple file formats and large document sets
- Build knowledge bases with vector search capabilities

**Key Features:**

- Vector store creation and management
- Multi-format document support (PDF, DOCX, TXT, etc.)
- Automatic chunking and indexing
- Semantic search with relevance scoring

### 2. Code Interpreter - Data Analysis & Visualization

**[📊 Complete Guide](02-code-interpreter.md)** | **[💻 Exercise](exercises/exercise_2_code_interpreter.py)**

Enable your agents to perform data analysis, create visualizations, and solve complex computational problems. Learn to:

- Execute Python code dynamically within agent conversations
- Generate charts, graphs, and data visualizations
- Perform statistical analysis and data transformations
- Handle file uploads and data processing workflows

**Key Features:**

- Sandboxed Python execution environment
- File upload and download capabilities
- Matplotlib/Seaborn visualization support
- Pandas/NumPy data processing
- Persistent session state during conversations

### 3. Function Calling - Custom Business Logic

**[⚙️ Complete Guide](03-function-calling.md)** | **[💻 Exercise](exercises/exercise_3_function_calling.py)**

Extend your agents with custom business logic, API integrations, and real-time data processing. Learn to:

- Define and register custom Python functions
- Implement parameter validation and error handling
- Build enterprise-grade business logic libraries
- Integrate with external APIs and services

**Key Features:**

- Automatic parameter extraction from natural language
- Type validation and error handling
- Real-time function execution
- External API integration patterns
- Multi-function orchestration

## 🔄 Tool Combination Patterns

### Pattern 1: Research & Analysis Workflow

```python
# 1. File Search: Find relevant documents
# 2. Code Interpreter: Analyze extracted data
# 3. Function Calling: Validate and store results
```

### Pattern 2: Data Processing Pipeline

```python
# 1. Function Calling: Fetch data from APIs
# 2. Code Interpreter: Process and visualize data
# 3. File Search: Compare with historical documents
```

### Pattern 3: Business Decision Support

```python
# 1. File Search: Retrieve policy documents
# 2. Function Calling: Apply business rules
# 3. Code Interpreter: Generate compliance reports
```

## 🎯 Module Exercises

### Exercise 1: Multi-Tool Integration

Build an agent that uses all three tools to solve a complex business scenario:

- Research market data using File Search
- Analyze trends with Code Interpreter
- Execute trading decisions with Function Calling

### Exercise 2: Enterprise Knowledge Assistant

Create a comprehensive knowledge management system:

- Index company documents with File Search
- Generate insights and summaries with Code Interpreter
- Integrate with CRM systems via Function Calling

### Exercise 3: Data Science Workflow

Implement an end-to-end data science pipeline:

- Load datasets through Function Calling
- Perform analysis with Code Interpreter
- Compare results with research papers via File Search

## 🔍 Best Practices

### Tool Selection Guidelines

1. **File Search** - When you need to:
   - Search through large document collections
   - Provide citations and references
   - Work with static knowledge bases
   - Implement RAG patterns

2. **Code Interpreter** - When you need to:
   - Perform data analysis or calculations
   - Generate visualizations or charts
   - Process uploaded files
   - Execute complex algorithms

3. **Function Calling** - When you need to:
   - Integrate with external systems
   - Execute custom business logic
   - Validate data or enforce rules
   - Perform real-time operations

### Performance Optimization

- **Combine tools strategically** to leverage each tool's strengths
- **Cache function results** to avoid redundant API calls
- **Optimize file search indexes** for faster retrieval
- **Use async patterns** for parallel tool execution

### Security Considerations

- **Validate all inputs** before processing
- **Implement access controls** for sensitive documents
- **Audit tool usage** for compliance requirements
- **Secure external API connections** with proper authentication

## 🔧 Troubleshooting

### Common Issues

**Tool configuration errors:**

- Verify tool definitions are properly formatted
- Check that required permissions are granted
- Ensure API keys and endpoints are correct

**Performance issues:**

- Monitor tool execution times
- Optimize file search indexes
- Implement caching strategies
- Consider async execution patterns

**Integration challenges:**

- Test tool combinations in isolation
- Implement proper error handling
- Add logging for debugging
- Use staging environments for testing

## 📈 Advanced Topics

### Custom Tool Development

Learn to build your own tools by extending the base tool classes and implementing custom logic patterns.

### Multi-Agent Tool Orchestration

Coordinate multiple agents with different tool specializations to solve complex business problems.

### Tool Performance Monitoring

Implement metrics and monitoring to track tool usage, performance, and effectiveness.

## ➡️ Next Steps

After mastering the tools in this module, you'll be ready to explore:

- **[Module 3: Orchestration](../03-orchestration/README.md)** - Advanced agent coordination patterns
- **[Module 4: MCP Integration](../04-mcp/README.md)** - Model Context Protocol for enhanced tool connectivity
- **[Module 5: Production Deployment](../05-production/README.md)** - Enterprise deployment and monitoring

## 🏆 Module Completion

You've completed Module 2 when you can:

✅ **Implement File Search** - Build RAG-enabled agents with document retrieval
✅ **Use Code Interpreter** - Create data analysis and visualization agents  
✅ **Develop Function Calling** - Integrate custom business logic and APIs
✅ **Combine Tools** - Orchestrate multiple tools for complex workflows
✅ **Optimize Performance** - Implement best practices for tool efficiency
✅ **Handle Errors** - Implement robust error handling and validation

---

**💡 Pro Tip**: The real power of Azure AI Foundry agents comes from combining tools strategically. File Search provides knowledge, Code Interpreter handles analysis, and Function Calling enables action - together they create comprehensive business solutions.
