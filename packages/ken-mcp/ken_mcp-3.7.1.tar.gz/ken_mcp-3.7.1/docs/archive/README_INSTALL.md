# ken-mcp Installation Guide

## Quick Install

```bash
pip install ken-mcp
```

## Verify Installation

After installing, verify everything is working:

```bash
ken-mcp verify
```

## Common Issues

### Linux: "No module named '_cffi_backend'"

This is the most common issue on Linux. Fix it by:

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-dev libffi-dev libssl-dev

   # Fedora/RHEL/CentOS
   sudo dnf install python3-devel libffi-devel openssl-devel

   # Arch Linux
   sudo pacman -S python libffi openssl base-devel

   # Alpine Linux
   sudo apk add python3-dev libffi-dev openssl-dev musl-dev gcc
   ```

2. **Reinstall Python packages:**
   ```bash
   pip install --upgrade --force-reinstall cffi cryptography
   pip install --upgrade ken-mcp
   ```

3. **Verify again:**
   ```bash
   ken-mcp verify
   ```

### Running Diagnostics

If you're still having issues:

```bash
ken-mcp diagnose
```

This will show:
- System information
- Missing dependencies
- Specific installation commands for your system
- Whether the MCP server can start

## Using with Claude Code

Once installation is verified, add to your Claude Code settings:

```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "ken-mcp-server"
    }
  }
}
```

## Manual Testing

To test the server manually:

```bash
# Start the server
ken-mcp-server

# In another terminal, you can interact with it
# The server will show available tools and their descriptions
```

## Need Help?

1. Run `ken-mcp diagnose` for detailed diagnostics
2. Check the error messages - they now include specific fix instructions
3. Make sure you have Python 3.8 or higher: `python --version`