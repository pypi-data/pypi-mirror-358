# Linux Installation Guide for ken-mcp

## Prerequisites

ken-mcp requires system libraries for cryptography support. Install these first:

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3-dev libffi-dev libssl-dev build-essential
```

### Fedora/RHEL/CentOS
```bash
sudo dnf install -y python3-devel libffi-devel openssl-devel gcc
```

### Alpine Linux
```bash
sudo apk add python3-dev libffi-dev openssl-dev musl-dev gcc
```

### Arch Linux
```bash
sudo pacman -S python libffi openssl base-devel
```

## Installation Steps

1. **Install system dependencies** (see above for your distribution)

2. **Install ken-mcp**:
```bash
pip install ken-mcp
```

3. **If you get CFFI errors**, reinstall the Python packages:
```bash
pip install --upgrade --force-reinstall cffi cryptography authlib
```

4. **Test the installation**:
```bash
# Check if it runs
ken-mcp-server --help

# Or test with Python
python3 -c "from ken_mcp.server import main; print('✅ Installation successful')"
```

## Troubleshooting

### "No module named '_cffi_backend'"
This means the CFFI library wasn't compiled properly. Solution:
```bash
# Remove and reinstall
pip uninstall -y cffi cryptography
pip install --no-binary :all: cffi
pip install cryptography
```

### "error: Microsoft Visual C++ 14.0 is required" (WSL)
If using WSL, install build tools:
```bash
sudo apt-get install build-essential
```

### Permission errors
Use `--user` flag or virtual environment:
```bash
# User installation
pip install --user ken-mcp

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install ken-mcp
```

## Claude Code Configuration

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "ken-mcp-server"
    }
  }
}
```

Or if using virtual environment:
```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "/path/to/venv/bin/ken-mcp-server"
    }
  }
}
```

## Verifying MCP Connection

1. Start Claude Code
2. Check the MCP connection status
3. If it fails, check logs for specific error messages
4. Run `ken-mcp-server` manually to see any error output