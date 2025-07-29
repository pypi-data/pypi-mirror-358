#!/usr/bin/env python3
"""Debug script to test MCP server loading"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Working directory: {os.getcwd()}")
print("\nAttempting imports...")

try:
    import fastmcp
    print(f"✅ fastmcp imported successfully from: {fastmcp.__file__}")
    print(f"   fastmcp version: {getattr(fastmcp, '__version__', 'unknown')}")
except ImportError as e:
    print(f"❌ Failed to import fastmcp: {e}")

try:
    from fastmcp import FastMCP, Context
    print("✅ FastMCP and Context imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FastMCP/Context: {e}")

try:
    import httpx
    print(f"✅ httpx imported successfully")
except ImportError as e:
    print(f"❌ Failed to import httpx: {e}")

try:
    import pydantic
    print(f"✅ pydantic imported successfully")
except ImportError as e:
    print(f"❌ Failed to import pydantic: {e}")

print("\nTesting MCP creation...")
try:
    mcp = FastMCP(name="debug-test")
    print("✅ MCP instance created successfully")
    
    @mcp.tool
    async def test_tool(ctx: Context, message: str) -> dict:
        """Test tool"""
        return {"message": f"Echo: {message}"}
    
    print("✅ Tool registered successfully")
    
except Exception as e:
    print(f"❌ Failed to create MCP: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")