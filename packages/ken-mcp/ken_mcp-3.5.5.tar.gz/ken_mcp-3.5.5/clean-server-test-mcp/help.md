# clean-server-test-mcp - Cross-Platform Setup & Troubleshooting Guide

## 🚀 Universal Quick Start (All Operating Systems)

### Step 1: Run Cross-Platform Diagnostics
```bash
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
python3 diagnose.py
```
**This will detect your OS and provide platform-specific instructions!**

### Step 2: Install Dependencies

#### Windows:
```cmd
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
py -m pip install -r requirements.txt
# OR
python -m pip install -r requirements.txt
```

#### macOS/Linux:
```bash
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
python3 -m pip install -r requirements.txt
# OR
pip3 install -r requirements.txt
```

### Step 3: Test the MCP Works
```bash
python3 test.py    # macOS/Linux
py test.py         # Windows
```
Expected: All tests should pass ✅

### Step 4: Add to Claude Code

#### Windows:
```cmd
# Primary method (recommended):
claude mcp add clean-server-test-mcp "py /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp\run_server.py"

# Alternative methods if above fails:
claude mcp add clean-server-test-mcp "/Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp\run_server.bat"
claude mcp add clean-server-test-mcp "python /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp\run_server.py"
```

#### macOS/Linux:
```bash
# Primary method (recommended):
claude mcp add clean-server-test-mcp "/Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/run_server.py"

# Alternative methods if above fails:
claude mcp add clean-server-test-mcp "python3 /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/run_server.py"
claude mcp add clean-server-test-mcp "/Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/run_server.sh"
```

### Step 5: Restart Claude Code
**CRITICAL:** Exit Claude Code completely and restart:
```bash
# Type 'exit' or press Ctrl+C, then run:
claude
```

### Step 6: Verify Connection
```bash
claude mcp list
# Should show: ✓ clean-server-test-mcp    Active

# In Claude Code, use:
/mcp
# Should show your MCP as connected ✔
```

### Step 7: Use Your MCP
Your MCP tools are now available in Claude Code conversations!

---

## 🆘 Quick Troubleshooting

### If MCP Shows as "Failed":
1. **Run diagnostics:** `python3 diagnose.py` (shows OS-specific fixes)
2. **Check Python:** Make sure you have Python 3.8+ installed
3. **Try alternative commands:** Use the backup methods from Step 4
4. **Check paths:** Ensure all file paths are correct for your OS
5. **Restart required:** Always restart Claude Code after changes

### Platform-Specific Issues:

#### Windows:
- Install Python from python.org or Microsoft Store
- Use `py` command instead of `python3`
- Use backslashes `\` in paths
- Try running as Administrator if permissions fail

#### macOS:
- Install Python via Homebrew: `brew install python@3.10`
- Use forward slashes `/` in paths  
- Make sure scripts are executable: `chmod +x run_server.py`

#### Linux:
- Install Python: `sudo apt install python3.10` (Ubuntu/Debian)
- Use forward slashes `/` in paths
- Make sure scripts are executable: `chmod +x run_server.py`
- Check firewall/permissions if issues persist

---

## 📱 Need Help?

**Run the diagnostic tool - it detects your exact setup:**
```bash
python3 diagnose.py
```

This provides customized instructions for your operating system and Python installation!
### Testing the MCP Server
```bash
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp

# Run the automated test suite
python3 test.py

# Expected output:
# ==================================================
# 🧪 Running MCP Server Tests for clean-server-test-mcp
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

### Step 1: Run Automatic Diagnostics

We've included a diagnostic script that checks for common issues:

```bash
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
python3 diagnose.py
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
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
python3 server.py
```

### Step 3: Common Fixes (Try in Order)

#### 1. Wrong Python Command (Most Common)
```bash
# Find your Python
which python3

# Remove and re-add with correct Python
claude mcp remove clean-server-test-mcp
# EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'

# Try different Python commands:
claude mcp add clean-server-test-mcp "python3 /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py"
# OR
claude mcp add clean-server-test-mcp "/usr/bin/python3 /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py"
# OR
claude mcp add clean-server-test-mcp "python3.11 /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py"

# EXIT Claude Code and restart again
```

#### 2. Missing Dependencies
```bash
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
pip install -r requirements.txt

# If you get "externally managed environment" error:
pip install --user -r requirements.txt
# OR create a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Wrong File Path
```bash
# Verify the exact path
ls -la /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py

# Use absolute path when adding
claude mcp add clean-server-test-mcp "python3 $(pwd)/server.py"
```

#### 4. Permission Issues
```bash
chmod +x /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py
```

#### 5. Python Version Conflicts
```bash
# This MCP requires Python >= 3.10
# Check your version:
python3 --version

# If too old, use a newer Python:
claude mcp add clean-server-test-mcp "python3.11 /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py"
```

### Step 4: Virtual Environment (If Other Fixes Fail)
```bash
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Use venv Python in Claude
claude mcp remove clean-server-test-mcp
# EXIT and restart Claude Code
claude mcp add clean-server-test-mcp "/Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/venv/bin/python /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py"
# EXIT and restart Claude Code
```

## 📋 Quick Fix Checklist

Run through this checklist when troubleshooting:

□ Run diagnostics: `cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp && python3 diagnose.py`
□ Fix any issues reported by diagnostics
□ Test manually: `python3 server.py`
□ Check Python path: `which python3`
□ Install dependencies: `pip install -r requirements.txt`
□ Use absolute paths in `claude mcp add`
□ EXIT and restart Claude Code after EVERY change
□ Check MCP status: `claude mcp list`

## 🔍 About the Diagnostic Script

The `diagnose.py` script included in this project checks for:
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
claude mcp remove clean-server-test-mcp
# EXIT Claude Code (type 'exit' or Ctrl+C)

# Make any changes to the code if needed
cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
# Edit files...

# Reinstall dependencies if needed
pip install -r requirements.txt

# Re-add the MCP
claude mcp add clean-server-test-mcp "python3 /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp/server.py"
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
   cd /Users/kenkai/ClaudeCode/MCP/clean-server-test-mcp
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
