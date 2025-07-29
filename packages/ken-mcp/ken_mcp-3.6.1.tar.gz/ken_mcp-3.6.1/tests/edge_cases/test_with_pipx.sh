#!/bin/bash
# Run edge case tests using pipx's Python that has fastmcp installed

echo "Running KEN-MCP edge case tests with pipx Python..."
echo "=================================================="

# Use the Python from pipx that has fastmcp
PIPX_PYTHON="/Users/kenkai/.local/pipx/venvs/fastmcp/bin/python3"

# First, let's inject our ken_mcp package into the pipx environment
echo "Setting up ken_mcp in pipx environment..."
cd /Users/kenkai/ClaudeCode/MCP

# Run our test script with the pipx Python
echo "Running edge case generation tests..."
$PIPX_PYTHON test_edge_cases/run_edge_case_test.py