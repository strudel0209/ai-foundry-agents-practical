#!/usr/bin/env python3
"""
Exercise 1: Basic MCP Server Implementation
===========================================

This exercise demonstrates the fundamentals of creating a Model Context Protocol (MCP) server.
MCP allows agents to securely connect to external data sources and services.

Learning Objectives:
- Understand MCP architecture and communication patterns
- Create a basic MCP server with tools and resources
- Implement server-side MCP protocol handling
- Test MCP server functionality
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import uuid

# MCP protocol message types
@dataclass
class MCPMessage:
    """Base MCP message structure"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class BasicMCPServer:
    """
    Basic MCP Server implementation demonstrating core concepts
    """
    
    def __init__(self):
        self.tools = {}
        self.resources = {}
        self.sessions = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server with capabilities"""
        self.logger.info("Initializing MCP server...")
        
        # Register built-in tools
        await self._register_tools()
        
        # Register built-in resources
        await self._register_resources()
        
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "BasicMCPServer",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            }
        }
    
    async def _register_tools(self):
        """Register available tools"""
        self.tools = {
            "echo": {
                "name": "echo",
                "description": "Echo back the input text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to echo back"
                        }
                    },
                    "required": ["text"]
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "Perform basic arithmetic calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                        }
                    },
                    "required": ["expression"]
                }
            },
            "current_time": {
                "name": "current_time",
                "description": "Get the current date and time",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    async def _register_resources(self):
        """Register available resources"""
        self.resources = {
            "server_info": {
                "uri": "mcp://server/info",
                "name": "Server Information",
                "description": "Information about this MCP server",
                "mimeType": "application/json"
            },
            "tools_list": {
                "uri": "mcp://server/tools",
                "name": "Available Tools",
                "description": "List of all available tools",
                "mimeType": "application/json"
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            self.logger.info(f"Handling request: {method}")
            
            # Route request to appropriate handler
            if method == "initialize":
                result = await self.initialize()
            elif method == "tools/list":
                result = await self.list_tools()
            elif method == "tools/call":
                result = await self.call_tool(params)
            elif method == "resources/list":
                result = await self.list_resources()
            elif method == "resources/read":
                result = await self.read_resource(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": list(self.tools.values())
        }
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Execute the tool
        if tool_name == "echo":
            result = await self._execute_echo(arguments)
        elif tool_name == "calculate":
            result = await self._execute_calculate(arguments)
        elif tool_name == "current_time":
            result = await self._execute_current_time(arguments)
        else:
            raise ValueError(f"Tool not implemented: {tool_name}")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        }
    
    async def _execute_echo(self, arguments: Dict[str, Any]) -> str:
        """Execute echo tool"""
        text = arguments.get("text", "")
        return f"Echo: {text}"
    
    async def _execute_calculate(self, arguments: Dict[str, Any]) -> str:
        """Execute calculate tool"""
        expression = arguments.get("expression", "")
        try:
            # Simple evaluation - in production, use a safer approach
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _execute_current_time(self, arguments: Dict[str, Any]) -> str:
        """Execute current_time tool"""
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources"""
        return {
            "resources": list(self.resources.values())
        }
    
    async def read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a resource"""
        uri = params.get("uri")
        
        if uri == "mcp://server/info":
            content = {
                "name": "BasicMCPServer",
                "version": "1.0.0",
                "description": "A basic MCP server for learning",
                "uptime": "N/A"
            }
        elif uri == "mcp://server/tools":
            content = self.tools
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(content, indent=2)
                }
            ]
        }

class MCPServerTest:
    """Test the MCP server functionality"""
    
    def __init__(self):
        self.server = BasicMCPServer()
        self.logger = logging.getLogger(__name__)
    
    async def run_tests(self):
        """Run comprehensive tests"""
        print("🚀 Starting MCP Server Tests...")
        
        # Test 1: Initialize server
        await self._test_initialize()
        
        # Test 2: List tools
        await self._test_list_tools()
        
        # Test 3: Call tools
        await self._test_call_tools()
        
        # Test 4: List resources
        await self._test_list_resources()
        
        # Test 5: Read resources
        await self._test_read_resources()
        
        print("✅ All tests completed!")
    
    async def _test_initialize(self):
        """Test server initialization"""
        print("\n📋 Test 1: Server Initialization")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Initialize response: {json.dumps(response, indent=2)}")
    
    async def _test_list_tools(self):
        """Test listing tools"""
        print("\n🔧 Test 2: List Tools")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Tools list: {len(response['result']['tools'])} tools available")
        for tool in response['result']['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
    
    async def _test_call_tools(self):
        """Test calling tools"""
        print("\n⚙️ Test 3: Call Tools")
        
        # Test echo tool
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "text": "Hello, MCP!"
                }
            }
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Echo tool: {response['result']['content'][0]['text']}")
        
        # Test calculate tool
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {
                    "expression": "2 + 3 * 4"
                }
            }
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Calculate tool: {response['result']['content'][0]['text']}")
        
        # Test current_time tool
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "current_time",
                "arguments": {}
            }
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Current time tool: {response['result']['content'][0]['text']}")
    
    async def _test_list_resources(self):
        """Test listing resources"""
        print("\n📚 Test 4: List Resources")
        
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/list",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Resources list: {len(response['result']['resources'])} resources available")
        for resource in response['result']['resources']:
            print(f"  - {resource['name']}: {resource['description']}")
    
    async def _test_read_resources(self):
        """Test reading resources"""
        print("\n📖 Test 5: Read Resources")
        
        # Test reading server info
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "resources/read",
            "params": {
                "uri": "mcp://server/info"
            }
        }
        
        response = await self.server.handle_request(request)
        print(f"✓ Server info resource read successfully")
        print(f"  Content: {response['result']['contents'][0]['text']}")

async def main():
    """Main execution function"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎓 MCP Server Exercise 1: Basic MCP Server")
    print("=" * 50)
    
    # Run tests
    tester = MCPServerTest()
    await tester.run_tests()
    
    print("\n🎯 Learning Summary:")
    print("- Implemented basic MCP server with tools and resources")
    print("- Handled MCP protocol messages (JSON-RPC 2.0)")
    print("- Created tools for echo, calculate, and current_time")
    print("- Implemented resource reading capabilities")
    print("- Tested all server functionality")
    
    print("\n🔗 Next Steps:")
    print("- Try exercise_2_business_mcp.py for business integration")
    print("- Explore real-world MCP server implementations")
    print("- Learn about MCP client integration with agents")

if __name__ == "__main__":
    asyncio.run(main())
