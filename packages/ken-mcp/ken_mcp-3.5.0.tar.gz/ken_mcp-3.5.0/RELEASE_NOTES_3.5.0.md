# KEN-MCP v3.5.0 Release Notes

## 🎯 Critical Fix: MCP Connection Issues Resolved

### Problem Discovered
Generated MCP servers were failing to connect in Claude Code due to stdout pollution from FastMCP deprecation warnings. This was breaking the JSON-RPC protocol communication.

### Solution Implemented
KEN-MCP now generates a `run_server.py` wrapper script for all MCPs that:
- Suppresses deprecation warnings before importing
- Ensures clean stdout for JSON-RPC protocol
- Maintains the same stdout redirection pattern in server.py

## 🔄 Changes in v3.5.0

### New Files Generated
- **`run_server.py`** - Wrapper script that runs the MCP with clean stdout
  - Automatically made executable
  - Suppresses Python deprecation warnings
  - Ensures proper module importing

### Updated Templates
- **Help documentation** - Now uses `run_server.py` instead of direct `server.py`
- **README** - Updated Claude command to use wrapper script
- **Diagnostics** - Added check for wrapper script existence
- **Validation** - Includes `run_server.py` in required files list

### Updated Instructions
All generated MCPs now show:
```bash
claude mcp add <name> "/path/to/run_server.py"
```
Instead of the previous:
```bash
claude mcp add <name> "python3 /path/to/server.py"
```

## 🚀 Upgrade Instructions

1. Update KEN-MCP:
   ```bash
   pip install --upgrade ken-mcp
   ```

2. For existing MCPs that fail to connect:
   - Generate a new MCP with v3.5.0 to get the wrapper script
   - Copy the `run_server.py` to your existing MCP directory
   - Update your Claude configuration to use `run_server.py`

## 🔍 Technical Details

The issue was caused by FastMCP emitting deprecation warnings to stdout when using `log_level` parameter in the constructor. These warnings corrupted the JSON-RPC protocol stream. The wrapper script filters these warnings before they can reach stdout.

## ✅ Verification

All newly generated MCPs will:
- Pass diagnostic checks
- Connect successfully to Claude Code
- Maintain clean JSON-RPC communication