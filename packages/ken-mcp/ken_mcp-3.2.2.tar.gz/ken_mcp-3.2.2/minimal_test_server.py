#!/usr/bin/env python3
"""Minimal test MCP server to verify Claude integration"""

from fastmcp import FastMCP, Context

# Create server with minimal config
mcp = FastMCP(
    name="minimal-test",
    instructions="A minimal test server"
)

@mcp.tool
async def echo(ctx: Context, message: str) -> dict:
    """Echo back a message"""
    return {"echoed": message}

# This is critical - without this, the server won't run
if __name__ == "__main__":
    mcp.run()