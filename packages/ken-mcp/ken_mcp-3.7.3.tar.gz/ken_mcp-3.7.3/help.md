# weather-monitor MCP Server - Complete Setup & Troubleshooting Guide

## 🚀 Quick Start

### 1. Test the MCP Server
```bash
# Run the test suite
cd /Users/kenkai/ClaudeCode/MCP
python3 scripts/test.py

# Check for implementation issues
python3 scripts/verify.py

# Run diagnostics if there are issues
python3 scripts/diagnose.py
```

### 2. Add to Claude Code
```bash
# Add the MCP to Claude Code (Global - Recommended)
claude mcp add weather-monitor -s user "/Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"

# Alternative (Local - only works from current directory)
# claude mcp add weather-monitor "/Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"

# Exit Claude Code (type 'exit' or press Ctrl+C)
# Restart Claude Code
claude

# Check that it's active
claude mcp list
# Should show: ✓ weather-monitor (Active)

# 💡 Global (-s user) = Works from any directory
# 💡 Local (no flag) = Only works from current directory
```

### 3. Verify Connection
In Claude Code, type: `/mcp`
You should see: `✔ weather-monitor` (connected)


## 🧪 Testing the MCP Server

### Automated Testing
```bash
cd /Users/kenkai/ClaudeCode/MCP

# Run the full test suite
python3 scripts/test.py

# Expected output:
# ==================================================
# 🧪 Running MCP Server Tests for weather-monitor
# ==================================================
# Testing server initialization...
#   ✅ Server initialization test passed
# Testing tool_one...
#   ✅ Valid input test passed
# ... more tests ...
# ==================================================
# 📊 Test Summary: X/Y passed
# ==================================================
```

### Implementation Verification
```bash
# Check for incomplete implementations
python3 scripts/verify.py

# This finds:
# - TODO/FIXME comments that need completion
# - Placeholder/mock data that needs replacing
# - Empty function implementations
# - Missing required resources
```

### Manual Testing
```bash
cd /Users/kenkai/ClaudeCode/MCP/weather-monitor

# Test the server directly
./run_server.py
# Should start without errors and wait for JSON-RPC input
# Press Ctrl+C to stop
```

## 🔧 Troubleshooting Failed MCP Connection

If the MCP shows as "Failed" in Claude Code, follow these steps:

### Step 1: Run Automatic Diagnostics

We've included a diagnostic script that checks for common issues:

```bash
cd /Users/kenkai/ClaudeCode/MCP
python3 scripts/diagnose.py
```

This will check:
- ✅ Python version compatibility
- ✅ All dependencies installed
- ✅ No print() statements breaking the protocol
- ✅ Proper logging configuration
- ✅ Server syntax and imports
- ✅ JSON-RPC compliance

Fix any ❌ failures shown, then re-run the diagnostic.

### Step 2: Manual System Diagnosis

If diagnostics pass but MCP still fails, run this comprehensive system check:

```bash
# Check MCP status
claude mcp list

# System information
echo "=== System Information ==="
uname -a
echo "Operating System: $(uname -s)"
echo "Architecture: $(uname -m)"

# Python availability
echo "=== Python Installation Analysis ==="
which python 2>/dev/null && python --version 2>/dev/null || echo "❌ python: not found"
which python3 2>/dev/null && python3 --version 2>/dev/null || echo "❌ python3: not found"

# Check specific Python versions
for version in 3.8 3.9 3.10 3.11 3.12; do
    cmd="python${version}"
    if which "$cmd" >/dev/null 2>&1; then
        echo "✅ $cmd: $($cmd --version 2>/dev/null)"
    else
        echo "❌ $cmd: not found"
    fi
done

# Test the MCP directly
cd /Users/kenkai/ClaudeCode/MCP/weather-monitor
./run_server.py
```

### Step 3: Common Fixes (Try in Order)

#### 1. Wrong Python Command (Most Common)
```bash
# Find your Python
which python3

# Remove and re-add with correct Python
claude mcp remove weather-monitor
# EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'

# Try different methods (Global scope - recommended):
claude mcp add weather-monitor -s user "/Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"
# OR (with Python prefix if needed)
claude mcp add weather-monitor -s user "python3 /Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"
# OR
claude mcp add weather-monitor -s user "/usr/bin/python3 /Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"

# Alternative (Local scope - only works from current directory):
# claude mcp add weather-monitor "/Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"

# EXIT Claude Code and restart again
```

#### 2. Missing Dependencies
```bash
cd /Users/kenkai/ClaudeCode/MCP/weather-monitor

# Modern Linux (Ubuntu 22.04+, Debian 12+) - recommended method
python3 -m pip install --user --break-system-packages -r requirements.txt

# If you get "externally managed environment" error, try these options:
# Option 1: Use --break-system-packages (recommended)
python3 -m pip install --user --break-system-packages -r requirements.txt

# Option 2: Create a virtual environment (best for development)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 3: System packages (if available)
sudo apt install python3-fastmcp python3-httpx python3-pydantic

# Option 4: Older Linux systems
python3 -m pip install --user -r requirements.txt
```

#### 3. Wrong File Path
```bash
# Verify the exact path
ls -la /Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py

# Use absolute path when adding
claude mcp add weather-monitor -s user "$(pwd)/weather-monitor/run_server.py"
```

#### 4. Permission Issues
```bash
chmod +x /Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py
```

#### 5. Python Version Conflicts
```bash
# This MCP requires Python >= 3.10
# Check your version:
python3 --version

# If too old, use a newer Python:
claude mcp add weather-monitor -s user "python3.11 /Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"
```

### Step 4: Virtual Environment (If Other Fixes Fail)
```bash
cd /Users/kenkai/ClaudeCode/MCP/weather-monitor
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Use venv Python in Claude
claude mcp remove weather-monitor
# EXIT and restart Claude Code
claude mcp add weather-monitor -s user "/Users/kenkai/ClaudeCode/MCP/weather-monitor/venv/bin/python /Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"
# EXIT and restart Claude Code
```

## 📋 Quick Fix Checklist

Run through this checklist when troubleshooting:

□ Run diagnostics: `cd /Users/kenkai/ClaudeCode/MCP && python3 scripts/diagnose.py`
□ Fix any issues reported by diagnostics
□ Test manually: `cd /Users/kenkai/ClaudeCode/MCP/weather-monitor && ./run_server.py`
□ Check Python path: `which python3`
□ Install dependencies: `cd /Users/kenkai/ClaudeCode/MCP/weather-monitor && pip install -r requirements.txt`
□ Use absolute paths in `claude mcp add` with `-s user` for global access
□ EXIT and restart Claude Code after EVERY change
□ Check MCP status: `claude mcp list`

## 🔍 About the Diagnostic Script

The `scripts/diagnose.py` script included in this project checks for:
- **Protocol Issues**: print() statements that break JSON-RPC
- **Dependencies**: Missing packages that prevent startup
- **Configuration**: Proper logging setup to stderr
- **Compatibility**: Python version requirements
- **Syntax**: Code errors that prevent loading

Always run diagnostics first when troubleshooting!
## 🔄 Managing This MCP

### Update/Reinstall
```bash
# Remove the MCP
claude mcp remove weather-monitor
# EXIT Claude Code (type 'exit' or Ctrl+C)

# Make any changes to the code if needed
cd /Users/kenkai/ClaudeCode/MCP/weather-monitor
# Edit files...

# Reinstall dependencies if needed
pip install -r requirements.txt

# Re-add the MCP
claude mcp add weather-monitor -s user "/Users/kenkai/ClaudeCode/MCP/weather-monitor/run_server.py"
# EXIT and restart Claude Code
```

### Check Status
```bash
claude mcp list
# ✓ = Active (working)
# ✗ = Failed (see troubleshooting above)
```

### View Logs
Check Claude Desktop logs for detailed error messages if the above steps don't resolve the issue.

## 🆘 Still Not Working?

If you've tried all the above and the MCP still shows as "Failed":

1. **Test the exact command Claude is using:**
   ```bash
   # Copy the exact command from 'claude mcp list' output
   # Run it directly to see the error
   ```

2. **Check for conflicting Python packages:**
   ```bash
   pip list | grep -E "(fastmcp|pydantic)"
   ```

3. **Try a completely fresh virtual environment:**
   ```bash
   cd /Users/kenkai/ClaudeCode/MCP/weather-monitor
   rm -rf venv
   python3 -m venv fresh_venv
   source fresh_venv/bin/activate
   pip install -e .
   ```

## 📝 Development Scripts

This project includes development tools in the `scripts/` directory:

- **`scripts/test.py`**: Comprehensive test suite for all MCP functionality
- **`scripts/verify.py`**: Checks for incomplete implementations and TODOs
- **`scripts/diagnose.py`**: Cross-platform diagnostic tool for troubleshooting

Always run these scripts from the root directory:
```bash
cd /Users/kenkai/ClaudeCode/MCP
python3 scripts/test.py
python3 scripts/verify.py
python3 scripts/diagnose.py
```

## 📝 Notes

- Always use absolute paths (full path starting with /)
- Python environment matters - Claude must use the same Python that has the dependencies
- "Failed" status is generic - always test manually to find the real error
- Some systems require specific Python versions or virtual environments

---
Generated by KEN-MCP - Comprehensive troubleshooting guide included
