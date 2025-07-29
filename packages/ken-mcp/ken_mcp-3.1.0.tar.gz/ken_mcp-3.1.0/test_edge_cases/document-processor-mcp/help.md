# document-processor-mcp - Setup & Troubleshooting Guide

## 🚀 Quick Start

### Adding to Claude Code
```bash
# Add the MCP server
claude mcp add document-processor-mcp "python3 test_edge_cases/document-processor-mcp/server.py"

# IMPORTANT: Exit and restart Claude Code
# Type 'exit' or press Ctrl+C, then run 'claude' again

# Verify it's active
claude mcp list
# Should show: ✓ document-processor-mcp    Active
```
### Testing the MCP Server
```bash
cd test_edge_cases/document-processor-mcp

# Run the automated test suite
python3 test.py

# Expected output:
# ==================================================
# 🧪 Running MCP Server Tests for document-processor-mcp
# ==================================================
# Testing server initialization...
#   ✅ Server initialization test passed
# Testing tool_one...
#   ✅ Valid input test passed
# ... more tests ...
# ==================================================
# 📊 Test Summary: X/Y passed
# ==================================================
# ✅ All tests passed! The MCP server is ready to use.
```

If any tests fail:
1. Check the error messages in the test output
2. Fix the implementation in server.py
3. Run the tests again until all pass

### Manual Testing
```bash
# Test the server directly (for debugging)
python3 server.py
# Expected output: "Server started on stdio"
# Press Ctrl+C to stop
```

## 🔧 Troubleshooting Failed MCP Connection

If the MCP shows as "Failed" in Claude Code, follow these steps:

### Step 1: System Diagnosis

Run this comprehensive system check:

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
cd test_edge_cases/document-processor-mcp
python3 server.py
```

### Step 2: Common Fixes (Try in Order)

#### 1. Wrong Python Command (Most Common)
```bash
# Find your Python
which python3

# Remove and re-add with correct Python
claude mcp remove document-processor-mcp
# EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'

# Try different Python commands:
claude mcp add document-processor-mcp "python3 test_edge_cases/document-processor-mcp/server.py"
# OR
claude mcp add document-processor-mcp "/usr/bin/python3 test_edge_cases/document-processor-mcp/server.py"
# OR
claude mcp add document-processor-mcp "python3.11 test_edge_cases/document-processor-mcp/server.py"

# EXIT Claude Code and restart again
```

#### 2. Missing Dependencies
```bash
cd test_edge_cases/document-processor-mcp
python3 -m pip install -e .

# If you get "externally managed environment" error:
python3 -m pip install --user -e .
# OR use pipx:
pipx install -e .
```

#### 3. Wrong File Path
```bash
# Verify the exact path
ls -la test_edge_cases/document-processor-mcp/server.py

# Use absolute path when adding
claude mcp add document-processor-mcp "python3 $(pwd)/server.py"
```

#### 4. Permission Issues
```bash
chmod +x test_edge_cases/document-processor-mcp/server.py
```

#### 5. Python Version Conflicts
```bash
# This MCP requires Python >= 3.10
# Check your version:
python3 --version

# If too old, use a newer Python:
claude mcp add document-processor-mcp "python3.11 test_edge_cases/document-processor-mcp/server.py"
```

### Step 3: Virtual Environment (If Other Fixes Fail)
```bash
cd test_edge_cases/document-processor-mcp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# Use venv Python in Claude
claude mcp remove document-processor-mcp
# EXIT and restart Claude Code
claude mcp add document-processor-mcp "test_edge_cases/document-processor-mcp/venv/bin/python test_edge_cases/document-processor-mcp/server.py"
# EXIT and restart Claude Code
```

## 📋 Quick Fix Checklist

Run through this checklist when troubleshooting:

□ Test manually: `cd test_edge_cases/document-processor-mcp && python3 server.py`
□ Check Python path: `which python3`
□ Install dependencies: `python3 -m pip install -e .`
□ Use absolute paths in `claude mcp add`
□ EXIT and restart Claude Code after EVERY change
□ Check MCP status: `claude mcp list`

## 🔄 Managing This MCP

### Update/Reinstall
```bash
# Remove the MCP
claude mcp remove document-processor-mcp
# EXIT Claude Code (type 'exit' or Ctrl+C)

# Make any changes to the code if needed
cd test_edge_cases/document-processor-mcp
# Edit files...

# Reinstall dependencies if needed
python3 -m pip install -e .

# Re-add the MCP
claude mcp add document-processor-mcp "python3 test_edge_cases/document-processor-mcp/server.py"
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
   cd test_edge_cases/document-processor-mcp
   rm -rf venv
   python3 -m venv fresh_venv
   source fresh_venv/bin/activate
   pip install -e .
   ```

## 📝 Notes

- Always use absolute paths (full path starting with /)
- Python environment matters - Claude must use the same Python that has the dependencies
- "Failed" status is generic - always test manually to find the real error
- Some systems require specific Python versions or virtual environments

---
Generated by KEN-MCP - Comprehensive troubleshooting guide included
