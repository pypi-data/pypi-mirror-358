#!/bin/bash

echo "Fixing Claude MCP configuration..."

# First, remove the problematic entry
echo "1. Removing todo-md-mcp..."
claude mcp remove todo-md-mcp

# Then add it correctly (all on one line)
echo "2. Adding todo-md-mcp correctly..."
claude mcp add todo-md-mcp "/usr/bin/python3.10 /home/ken/Project_Testing/create_mcp/todo-md-mcp/server.py"

# Verify
echo "3. Verifying configuration..."
claude mcp list

echo -e "\nDone! Now restart Claude Desktop for the changes to take effect."