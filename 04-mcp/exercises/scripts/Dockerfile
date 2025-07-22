FROM python:3.12-slim

# Cache busting argument
ARG CACHEBUST=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-mcp.txt .
RUN pip install --no-cache-dir -r requirements-mcp.txt

# Copy MCP server files
COPY setup_sqlite_mcp_server.py .
COPY create_business_database.py .

# Create directory for database
RUN mkdir -p mcp-config

# Create the database
RUN python create_business_database.py

# Expose port
EXPOSE 3000

# Run the MCP server
CMD ["python", "setup_sqlite_mcp_server.py", "--server-only", "--port", "3000"]
