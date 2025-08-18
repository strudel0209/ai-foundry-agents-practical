# SQLite MCP Server Setup

This guide shows how to use the official mcp-sqlite server with Azure AI Foundry agents.

## Prerequisites

- **Python 3.12+** for the Python mcp-sqlite package
- **OR** Node.js/npm for the JavaScript version
- **OR** Python 3.11+ for the reference implementation

## Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
python setup_sqlite_mcp_server.py
```

This script automatically:
1. Detects your Python version
2. Creates the database if needed
3. Runs the appropriate MCP server:
   - Python mcp-sqlite (if Python 3.12+)
   - Node.js version via npx (if Python < 3.12)
   - Shows alternatives if neither is available

### Option 2: Manual Setup

#### For Python 3.12+:
```bash
# Install the Python package
pip install git+https://github.com/panasenco/mcp-sqlite.git

# Create database
python create_business_database.py

# Run server
python -m mcp_sqlite ./mcp-config/business.db
```

#### For Python 3.11 (using Node.js):
```bash
# Create database
python create_business_database.py

# Run server using npx (Node.js required)
npx @modelcontextprotocol/server-sqlite ./mcp-config/business.db
```

#### For any Python version (reference implementation):
```bash
# Create database
python create_business_database.py

# Run the educational reference server
python simple_sqlite_mcp_server.py ./mcp-config/business.db
```

## MCP Inspector - Graphical Interface

MCP Inspector provides a web-based graphical interface to explore and test the SQLite MCP server before integrating with Azure AI Foundry agents.

### Quick Start with Inspector

```bash
# Launch MCP Inspector with SQLite server
python setup_sqlite_mcp_server.py --inspector
```

This will:
1. Start the SQLite MCP server
2. Launch MCP Inspector in your browser
3. Allow you to interactively test SQL queries
4. Show the JSON-RPC protocol communication

### Direct Inspector Commands

If you prefer to launch the inspector directly:

```bash
# With uvx (Python 3.12+)
npx @modelcontextprotocol/inspector uvx mcp-sqlite ./mcp-config/business.db -m ./mcp-config/metadata.json

# With Python module
npx @modelcontextprotocol/inspector python -m mcp_sqlite.server ./mcp-config/business.db -m ./mcp-config/metadata.json
```

### What You Can Do in MCP Inspector

1. **View Available Tools**: See the `query` tool exposed by the SQLite server
2. **Test SQL Queries**: Execute queries and see results in real-time
3. **Explore Protocol**: Understand the JSON-RPC messages for Azure AI integration
4. **Debug Issues**: See error messages and responses clearly

### Example Queries to Try in Inspector

```sql
-- Get all customers
SELECT * FROM customers;

-- Find high-value orders
SELECT o.*, c.name as customer_name 
FROM orders o 
JOIN customers c ON o.customer_id = c.id 
WHERE o.total > 500;

-- Product inventory status
SELECT name, stock, 
       CASE 
         WHEN stock < 20 THEN 'Low Stock'
         WHEN stock < 50 THEN 'Medium Stock'
         ELSE 'Good Stock'
       END as stock_status
FROM products;

-- Financial summary
SELECT year, quarter, revenue, profit, 
       ROUND(profit * 100.0 / revenue, 2) as profit_margin_pct
FROM financials 
ORDER BY year DESC, quarter DESC;
```

### Opening in Browser from Devcontainer

Since you're in a devcontainer, the browser won't open automatically. When you see the URL in the terminal:

1. **VS Code**: Click on the URL (it will be clickable)
2. **Manual**: Copy the URL and use: `$BROWSER <url>`
3. **Port Forward**: VS Code may automatically forward the port

## Python Version Requirements

The official `mcp-sqlite` Python package requires **Python 3.12 or higher** due to its dependencies on newer Python features. If you're using Python 3.11:

1. **Recommended**: Update your devcontainer to Python 3.12
2. **Alternative**: Use the Node.js version via npx
3. **Fallback**: Use the reference implementation (simple_sqlite_mcp_server.py)

## Installation

The mcp-sqlite package is automatically installed via requirements.txt:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install git+https://github.com/panasenco/mcp-sqlite.git
```

## How It Works

- The official mcp-sqlite server provides full MCP protocol support
- Communicates via stdio (standard input/output)
- Supports all SQLite features including views, indexes, and complex queries
- Azure AI agents can connect to it through the MCP tool configuration

## Testing the Database

You can explore the data directly:

```bash
# Install sqlite3 if not already available
sudo apt-get update && sudo apt-get install -y sqlite3

# Open SQLite console
sqlite3 ./mcp-config/business.db

# List all tables
.tables

# View recent financial data
SELECT * FROM financials ORDER BY year DESC, quarter DESC;

# Check customer orders
SELECT c.name, o.product, o.amount 
FROM customers c 
JOIN orders o ON c.id = o.customer_id;
```

Alternatively, you can use Python to explore the database:

```python
# Use Python's built-in sqlite3 module
python -c "
import sqlite3
conn = sqlite3.connect('./mcp-config/business.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print('Tables:', [row[0] for row in cursor.fetchall()])
"
```

## For Production Use

In production, you would:

1. Deploy the MCP server to Azure Container Apps or Azure Functions
2. Use Azure Managed Identity for authentication
3. Configure your agent with the deployed server's URL

## Testing the Integration

While the MCP server is running in one terminal, open another terminal and run:

```bash
python exercise_2_mcp_agents.py
```

## Why This Approach?

- **One Command**: Single script handles everything
- **Auto-setup**: Creates database if it doesn't exist
- **Visual Debugging**: MCP Inspector provides graphical interface
- **Clean Shutdown**: Handles Ctrl+C gracefully
- **No Installation**: npx handles the MCP server
- **Production Ready**: Same server can be containerized for deployment

## Business Use Cases

With the business database, agents can:
- Perform financial analysis and forecasting
- Create data visualizations
- Calculate business metrics and KPIs
- Identify trends and patterns
- Generate actionable insights

## Learn More

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP SQLite Server](https://mcpservers.org/servers/panasenco/mcp-sqlite)
- [Azure AI Foundry MCP Tools](https://learn.microsoft.com/azure/ai-foundry/agents/tools/model-context-protocol)
