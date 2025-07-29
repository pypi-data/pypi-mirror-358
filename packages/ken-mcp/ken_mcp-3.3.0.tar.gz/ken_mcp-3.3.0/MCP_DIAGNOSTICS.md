# MCP Diagnostics Guide

## Overview

The `diagnose_mcp_failure.py` script is a comprehensive diagnostic tool that identifies why MCP servers fail to load in Claude Code. It performs multiple checks to ensure your MCP server is properly configured and compatible with the MCP protocol.

## Usage

```bash
python3 diagnose_mcp_failure.py <path_to_mcp>

# Example:
python3 diagnose_mcp_failure.py ./my-mcp-server
```

## What It Checks

### 1. **Environment & Dependencies**
- ✅ Python version (3.10+ required)
- ✅ FastMCP installation
- ✅ All dependencies from pyproject.toml
- ✅ Module imports

### 2. **MCP Protocol Compliance**
- ✅ No print() statements (breaks JSON-RPC)
- ✅ Logging configured to stderr only
- ✅ Stdout redirection during imports
- ✅ JSON-RPC message format

### 3. **Code Quality**
- ✅ Syntax errors
- ✅ FastMCP API usage (tool.fn vs tool.function)
- ✅ Async/await patterns
- ✅ File permissions

### 4. **Runtime Testing**
- ✅ Server execution without errors
- ✅ JSON-RPC handshake simulation
- ✅ Import validation

## Common Issues & Fixes

### 1. **Print Statements Breaking Protocol**
```python
# ❌ BAD - Breaks MCP protocol
print("Starting server...")

# ✅ GOOD - Use logger
import logging
logger = logging.getLogger(__name__)
logger.info("Starting server...")
```

### 2. **Logging Configuration**
```python
# ✅ REQUIRED at top of server.py
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # CRITICAL: Must be stderr!
)
```

### 3. **Stdout Redirection**
```python
# ✅ Prevent library import pollution
_original_stdout = sys.stdout
sys.stdout = sys.stderr  # Redirect during imports

# Your imports here...

sys.stdout = _original_stdout  # Restore for MCP protocol
```

### 4. **FastMCP API Usage**
```python
# ❌ WRONG (old API)
tool_func = tool.function
resources = mcp._resources

# ✅ CORRECT
tool_func = tool.fn
resources = await mcp.get_resources()
```

## Diagnostic Output Example

```
🔍 MCP Failure Diagnostics
📁 Checking: /path/to/mcp

📊 DIAGNOSTIC RESULTS
============================================================
✅ [PATH] MCP directory exists
✅ [SYNTAX] server.py syntax
❌ [STDOUT] No print() statements
   → Found print() at lines: 10, 22, 29
❌ [LOGGING] Logging to stderr
   → Logging not configured to stderr

🔧 RECOMMENDED FIXES
------------------------------------------------------------
1. Replace all print() with logger.info()
2. Add logging configuration at top of server.py
```

## Critical Rules for MCP Servers

1. **NEVER use print()** - It corrupts the JSON-RPC protocol
2. **Always log to stderr** - Stdout is reserved for MCP communication
3. **Handle imports carefully** - Some libraries print during import
4. **Use correct FastMCP API** - Check documentation for current API
5. **Make server.py executable** - Required for Claude to run it

## Testing Your Fix

After fixing issues:

1. Re-run diagnostics:
   ```bash
   python3 diagnose_mcp_failure.py ./my-mcp-server
   ```

2. Test server directly:
   ```bash
   python3 ./my-mcp-server/server.py
   # Should show "Server started on stdio" in stderr
   ```

3. Add to Claude:
   ```bash
   claude mcp add my-server "python3 /path/to/server.py"
   # Exit and restart Claude
   claude mcp list  # Should show ✓ my-server Active
   ```

## If Still Failing

1. Check Claude logs:
   ```bash
   # macOS
   ~/Library/Logs/Claude/
   
   # Linux
   ~/.config/Claude/logs/
   ```

2. Run with debug logging:
   ```python
   logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
   ```

3. Test with minimal MCP:
   ```python
   #!/usr/bin/env python3
   import sys
   import logging
   from fastmcp import FastMCP
   
   logging.basicConfig(level=logging.INFO, stream=sys.stderr)
   sys.stdout = sys.stderr
   
   mcp = FastMCP("test")
   sys.stdout = sys.__stdout__
   
   if __name__ == "__main__":
       mcp.run()
   ```

## Summary

The diagnostic script helps identify and fix the most common MCP loading issues:
- **Stdout pollution** from print() statements
- **Missing dependencies** or wrong Python version
- **Incorrect API usage** with FastMCP
- **Import-time errors** that prevent loading

Always run diagnostics after generating or modifying an MCP server to ensure compatibility with Claude.