# KEN-MCP Diagnostic Guide

## Common Issues When MCP Fails to Connect in Claude Code

### 1. **Check Installation**
```bash
# Verify ken-mcp is installed
pip show ken-mcp

# Check version (should be 3.0.0 or later)
pip list | grep ken-mcp
```

### 2. **Verify Dependencies**
```bash
# Check if all dependencies are installed
pip show fastmcp httpx pydantic

# If missing, install them:
pip install fastmcp httpx pydantic
```

### 3. **Test MCP Server Manually**
```bash
# Method 1: Using the installed command
ken-mcp-server

# Method 2: Using Python module
python -m ken_mcp.server

# Method 3: Direct Python
python -c "from ken_mcp.server import main; main()"
```

### 4. **Check Claude Code Configuration**
Your Claude Code MCP configuration should look like:
```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "ken-mcp-server"
    }
  }
}
```

Or with full path:
```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "python",
      "args": ["-m", "ken_mcp.server"]
    }
  }
}
```

### 5. **Common Error Messages and Solutions**

#### "No module named 'fastmcp'"
- Solution: `pip install fastmcp`

#### "No module named 'ken_mcp'"
- Solution: `pip install ken-mcp`

#### "ImportError: cannot import name 'mcp' from 'ken_mcp.generator'"
- This means you have an older version. Update: `pip install --upgrade ken-mcp`

#### Server starts but no tools available
- The server is running but may not be exposing tools properly
- Check server output for error messages

### 6. **Debug Steps**
1. **Check Python version**: 
   ```bash
   python --version  # Should be 3.8 or higher
   ```

2. **Test imports manually**:
   ```python
   python -c "import ken_mcp; print('✅ ken_mcp imported')"
   python -c "from ken_mcp.generator import mcp; print('✅ MCP instance loaded')"
   python -c "from ken_mcp.server import main; print('✅ Server entry point OK')"
   ```

3. **Check for import errors**:
   ```bash
   python -c "import ken_mcp.generator" 2>&1
   ```

4. **Verbose server start**:
   ```bash
   python -m ken_mcp.server --verbose
   ```

### 7. **Linux-Specific Issues**

- **Python command**: Some Linux distros use `python3` instead of `python`
  ```json
  {
    "mcpServers": {
      "ken-mcp": {
        "command": "python3",
        "args": ["-m", "ken_mcp.server"]
      }
    }
  }
  ```

- **Virtual environment**: If using venv, specify full path:
  ```json
  {
    "mcpServers": {
      "ken-mcp": {
        "command": "/home/user/venv/bin/python",
        "args": ["-m", "ken_mcp.server"]
      }
    }
  }
  ```

### 8. **Get Server Logs**
Check Claude Code logs for more details about why the connection failed. The logs usually show the exact error message when trying to start the MCP server.