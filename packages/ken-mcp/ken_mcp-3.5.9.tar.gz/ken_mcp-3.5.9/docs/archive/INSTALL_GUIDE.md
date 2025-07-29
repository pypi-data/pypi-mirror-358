# Complete Installation Guide for ken-mcp

## Quick Install

```bash
pip install ken-mcp
```

## Verify Installation

After installing, always verify:

```bash
ken-mcp verify
```

## Platform-Specific Installation

### 🐧 Linux

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev libffi-dev libssl-dev build-essential

# Install ken-mcp
pip install ken-mcp

# If you get CFFI errors
pip install --upgrade --force-reinstall cffi cryptography
```

#### Fedora/RHEL/CentOS
```bash
# Install system dependencies
sudo dnf install python3-devel libffi-devel openssl-devel gcc

# Install ken-mcp
pip install ken-mcp
```

#### Arch Linux
```bash
# Install system dependencies
sudo pacman -S python libffi openssl base-devel

# Install ken-mcp
pip install ken-mcp
```

#### Alpine Linux
```bash
# Install system dependencies
sudo apk add python3-dev libffi-dev openssl-dev musl-dev gcc

# Install ken-mcp
pip install ken-mcp
```

### 🍎 macOS

```bash
# 1. Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# 2. If using Homebrew Python, install dependencies
brew install libffi openssl

# 3. Set environment variables (for M1/M2 Macs, paths might differ)
export LDFLAGS="-L$(brew --prefix openssl)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"

# 4. Install ken-mcp
pip install ken-mcp

# If you get errors, force reinstall cryptography
pip install --upgrade --force-reinstall cffi cryptography
```

#### Common macOS Issues

**M1/M2 Mac Issues:**
```bash
# Use arch-specific pip
arch -arm64 pip install ken-mcp
# or
arch -x86_64 pip install ken-mcp
```

**Homebrew Python vs System Python:**
```bash
# Make sure you're using the right Python
which python3
# Should show /opt/homebrew/bin/python3 or /usr/local/bin/python3
```

### 🪟 Windows

#### Option 1: Pre-compiled Wheels (Easiest)
```powershell
# Update pip first
python -m pip install --upgrade pip

# Install using pre-compiled wheels
pip install --only-binary :all: cffi cryptography
pip install ken-mcp
```

#### Option 2: Visual Studio Build Tools
1. Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Select "C++ build tools" workload
3. Install ken-mcp:
   ```powershell
   pip install ken-mcp
   ```

#### Option 3: Anaconda/Miniconda
```powershell
# If using Anaconda/Miniconda
conda install cffi cryptography
pip install ken-mcp
```

#### Common Windows Issues

**"Microsoft Visual C++ 14.0 is required":**
- Install Visual Studio Build Tools (Option 2 above)
- Or use pre-compiled wheels (Option 1)

**WSL (Windows Subsystem for Linux):**
- Follow the Linux instructions above

## 🔧 Troubleshooting

### Run Diagnostics
```bash
# Full diagnostic report
ken-mcp diagnose
```

### Common Errors

#### "No module named '_cffi_backend'"
This means CFFI wasn't compiled properly. The solution depends on your OS - run `ken-mcp-server` to see specific instructions for your platform.

#### "error: Microsoft Visual C++ 14.0 is required" (Windows)
Use pre-compiled wheels:
```powershell
pip install --only-binary :all: cffi cryptography
```

#### "fatal error: openssl/opensslv.h: No such file or directory" (Linux/macOS)
Install OpenSSL development headers (see platform-specific instructions above).

### Virtual Environments

Using a virtual environment can help avoid conflicts:

```bash
# Create virtual environment
python3 -m venv ken-mcp-env

# Activate it
# Linux/macOS:
source ken-mcp-env/bin/activate
# Windows:
ken-mcp-env\Scripts\activate

# Install ken-mcp
pip install ken-mcp
```

## 📋 Using with Claude Code

Once installed and verified, add to your Claude Code settings:

```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "ken-mcp-server"
    }
  }
}
```

For virtual environments:
```json
{
  "mcpServers": {
    "ken-mcp": {
      "command": "/path/to/venv/bin/ken-mcp-server"
    }
  }
}
```

## 🆘 Still Having Issues?

1. Check Python version: `python --version` (needs 3.8+)
2. Run `ken-mcp diagnose` for detailed diagnostics
3. Try in a fresh virtual environment
4. Check the specific error message - ken-mcp now provides platform-specific solutions

## 💡 Tips

- Always run `ken-mcp verify` after installation
- Use virtual environments to avoid conflicts
- On corporate networks, you may need to configure proxy settings
- The error messages now include specific commands for your OS