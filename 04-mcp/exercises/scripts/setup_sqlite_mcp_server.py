"""
Minimal MCP SQLite Server with Streamable HTTP Transport
Based on modern MCP patterns from 2025
"""

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

DB_PATH = "./mcp-config/business.db"

TOOLS = {
    "sql_query": {
        "description": "Execute SQL queries on the database",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute"},
                "params": {"type": "array", "items": {"type": "string"}, "description": "Query parameters"}
            },
            "required": ["query"]
        }
    },
    "list_tables": {
        "description": "List all tables in the database",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "table_schema": {
        "description": "Get schema for a table",
        "inputSchema": {
            "type": "object",
            "properties": {"table": {"type": "string", "description": "Table name"}},
            "required": ["table"]
        }
    }
}

def db_query(sql, params=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params or [])
        if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("PRAGMA"):
            return [dict(row) for row in cur.fetchall()]
        else:
            conn.commit()
            return {"affected": cur.rowcount}

class MCPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Session-ID, Authorization')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        self._set_headers()
        if path == "/health":
            self.wfile.write(json.dumps({
                "status": "healthy",
                "server": "sqlite-mcp",
                "protocol": "2025-03-26"
            }).encode())
        elif path == "/capabilities":
            self.wfile.write(json.dumps({
                "protocolVersion": "2025-03-26",
                "serverInfo": {"name": "sqlite-mcp", "version": "1.0"},
                "capabilities": {"tools": TOOLS}
            }).encode())
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ["/", "/mcp"]:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            return
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            req = json.loads(body)
        except Exception:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return
        resp = self.handle_mcp(req)
        self._set_headers()
        self.wfile.write((json.dumps(resp) + "\n").encode())

    def handle_mcp(self, req):
        method = req.get("method", "")
        params = req.get("params", {})
        req_id = req.get("id")
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": {"name": "sqlite-mcp", "version": "1.0"},
                        "capabilities": {"tools": TOOLS}
                    }
                }
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": name,
                                "description": info["description"],
                                "inputSchema": info["inputSchema"]
                            }
                            for name, info in TOOLS.items()
                        ]
                    }
                }
            elif method == "tools/call":
                tool = params.get("name")
                args = params.get("arguments", {})
                if tool == "sql_query":
                    query = args.get("query", "").strip()
                    if not query:
                        raise ValueError("Query parameter is required")
                    result = db_query(query, args.get("params"))
                elif tool == "list_tables":
                    result = db_query("SELECT name FROM sqlite_master WHERE type='table'")
                elif tool == "table_schema":
                    table = args.get("table", "").strip()
                    if not table:
                        raise ValueError("Table parameter is required")
                    result = db_query(f"PRAGMA table_info({table})")
                else:
                    raise ValueError(f"Unknown tool: {tool}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }],
                        "isError": False
                    }
                }
            elif method == "resources/list":
                tables = db_query("SELECT name FROM sqlite_master WHERE type='table'")
                resources = [
                    {
                        "uri": f"sqlite:///{row['name']}",
                        "name": row['name'],
                        "description": f"SQLite table: {row['name']}"
                    }
                    for row in tables
                ]
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"resources": resources}
                }
            elif method == "resources/read":
                uri = params.get("uri", "")
                if not uri.startswith("sqlite:///"):
                    raise ValueError("Invalid resource URI")
                table = uri.replace("sqlite:///", "")
                rows = db_query(f"SELECT * FROM {table}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [{
                            "type": "text",
                            "text": json.dumps(rows, indent=2)
                        }]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }

if __name__ == "__main__":
    print("🚀 Minimal MCP SQLite Server (HTTP)")
    print(f"📊 Database: {DB_PATH}")
    print("🌐 Listening on: http://0.0.0.0:3000")
    print("Endpoints: POST /mcp, GET /health, GET /capabilities")
    server = HTTPServer(('0.0.0.0', 3000), MCPHandler)
    server.serve_forever()