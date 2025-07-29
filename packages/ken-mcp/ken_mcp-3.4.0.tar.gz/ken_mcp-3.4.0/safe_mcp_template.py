#!/usr/bin/env python3
"""
Safe MCP Server Template
IMPORTANT: MCP servers communicate via JSON-RPC over stdio.
ANY print() or stdout output breaks the protocol!
"""

import sys
import logging

# Configure logging to use stderr ONLY (stdout is reserved for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Critical: log to stderr, not stdout!
)

logger = logging.getLogger(__name__)

# Suppress any stdout from imported libraries
import os
import io

# Redirect stdout to devnull during imports to catch any rogue prints
_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

try:
    # Your imports here
    from fastmcp import FastMCP, Context
    # ... other imports ...
finally:
    # Restore stdout for MCP communication
    sys.stdout.close()
    sys.stdout = _stdout

# Now create your MCP server
mcp = FastMCP(
    name="your-mcp-name",
    instructions="Your instructions"
)

# Your tools here...
@mcp.tool
async def example_tool(ctx: Context, message: str) -> dict:
    """Example tool - use logger, not print!"""
    logger.info(f"Tool called with: {message}")  # This goes to stderr
    # NEVER use print() here!
    return {"result": "success"}

# Critical: The main block
if __name__ == "__main__":
    # No prints here either!
    logger.info("Starting MCP server...")
    mcp.run()