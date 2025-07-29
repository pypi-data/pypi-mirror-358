# KEN-MCP Troubleshooting Guide

## Common Issues and Solutions

### 1. MCP Server Fails to Load in Claude Desktop

**Symptoms:**
- Error message: "Failed to load MCP server"
- Server doesn't appear in Claude's MCP list
- Claude shows connection errors

**Common Causes & Solutions:**

#### A. Python Path Issues
```bash
# Find your Python installation
which python3
which python3.10

# Update your Claude config with the correct path:
{
  "mcpServers": {
    "your-mcp": {
      "command": "/usr/bin/python3.10",  # Use full path
      "args": ["/path/to/your-mcp/server.py"]
    }
  }
}
```

#### B. Missing Dependencies
```bash
# Navigate to your generated MCP directory
cd /path/to/your-mcp

# Install dependencies
pip install -r requirements.txt
# OR
pip install fastmcp httpx pydantic
```

#### C. Import Errors
Check server.py for import issues:
```bash
# Test the server directly
python3 server.py

# Common fixes:
# 1. Install missing packages
# 2. Check Python version compatibility
# 3. Ensure fastmcp is installed
```

### 2. Generated Tests Fail

**Issue:** Tests use incorrect FastMCP API

**Fix Applied in v3.2.1:**
- Changed `mcp._tools` → `await mcp.get_tool("tool_name")`
- Changed `tool.function` → `tool.fn`
- Changed `mcp._resources` → `await mcp.get_resources()`
- Changed `mcp._prompts` → `await mcp.get_prompts()`

### 3. Placeholder Code Not Implemented

**Issue:** KEN-MCP generates skeleton code that needs implementation

**Solution:**
1. After generation, open the project in Claude Code
2. Ask Claude to implement the actual functionality:
   ```
   Please implement the actual logic for all the TODO sections in this MCP server based on the requirements
   ```
3. Claude will replace placeholder code with working implementations

### 4. Environment Variables Not Loading

**Issue:** Server expects environment variables but they're not set

**Solution:**
1. Create a `.env` file in your MCP directory
2. Add required variables:
   ```
   API_KEY=your-key-here
   DATABASE_URL=your-db-url
   ```
3. Ensure the server loads dotenv:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### 5. Server Syntax Errors

**Issue:** Generated code has syntax errors

**Quick Check:**
```bash
# Validate Python syntax
python3 -m py_compile server.py

# Run the server directly to see errors
python3 server.py
```

### 6. Claude Desktop Configuration Issues

**Correct Configuration Format:**
```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "python3",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "OPTIONAL_ENV_VAR": "value"
      }
    }
  }
}
```

**Common Mistakes:**
- Using relative paths (use absolute paths)
- Wrong Python command (use full path if needed)
- JSON syntax errors (validate with jsonlint)

### 7. Debugging Steps

1. **Test Server Standalone:**
   ```bash
   cd /path/to/your-mcp
   python3 server.py
   ```

2. **Check Claude Logs:**
   - macOS: `~/Library/Logs/Claude/`
   - Look for MCP-related errors

3. **Verbose Mode:**
   Add logging to your server:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Validate MCP Protocol:**
   ```bash
   # Install mcp-cli if available
   mcp-cli test /path/to/server.py
   ```

### 8. Version Compatibility

**Ensure Compatibility:**
- Python ≥ 3.8 (3.10+ recommended)
- fastmcp ≥ 0.1.0
- Latest Claude Desktop version

**Check Versions:**
```bash
python3 --version
pip show fastmcp
```

### 9. Clean Reinstall

If all else fails:
```bash
# Remove old installation
pip uninstall ken-mcp fastmcp

# Clean install
pip install ken-mcp --upgrade
pip install fastmcp --upgrade
```

## Getting Help

1. **Check Generated Logs:**
   - Look for `test.py` output
   - Run tests to identify issues

2. **Community Support:**
   - Report issues: https://github.com/ken-mcp/ken-mcp/issues
   - Include error messages and Python version

3. **Quick Fixes:**
   - Regenerate with latest ken-mcp version
   - Use Claude Code to fix implementation issues
   - Ensure all dependencies are installed

## Prevention Tips

1. Always test generated servers before adding to Claude
2. Use virtual environments for isolation
3. Keep dependencies up to date
4. Follow the two-step process: Generate → Implement with Claude