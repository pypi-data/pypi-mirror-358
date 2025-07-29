# Complete Error Scenarios for ken-mcp

## 🐧 Linux-Specific Errors

### 1. CFFI Backend Error
**Error**: `ModuleNotFoundError: No module named '_cffi_backend'`
**Covered**: ✅ Yes
**Solution**: Install system dependencies based on distribution

### 2. Missing Development Headers
**Error**: `fatal error: Python.h: No such file or directory`
**Covered**: ✅ Yes
**Solution**: Install python3-dev/python3-devel

### 3. OpenSSL Headers Missing
**Error**: `fatal error: openssl/opensslv.h: No such file or directory`
**Covered**: ✅ Yes
**Solution**: Install libssl-dev/openssl-devel

### 4. Permission Denied
**Error**: `Permission denied: '/usr/local/lib/python3.x/...'`
**Covered**: ✅ Yes
**Solution**: Use --user flag or virtual environment

### 5. GLIBC Version Mismatch
**Error**: `version 'GLIBC_2.xx' not found`
**Covered**: ❌ Should add
**Solution**: Use older cryptography version or update system

## 🍎 macOS-Specific Errors

### 1. Xcode Command Line Tools Missing
**Error**: `xcrun: error: invalid active developer path`
**Covered**: ✅ Yes
**Solution**: xcode-select --install

### 2. Architecture Mismatch (M1/M2)
**Error**: `mach-o file, but is an incompatible architecture`
**Covered**: ✅ Yes
**Solution**: Use arch-specific pip commands

### 3. Homebrew vs System Python Conflicts
**Error**: `Library not loaded: @rpath/libssl.dylib`
**Covered**: ✅ Yes
**Solution**: Set LDFLAGS/CPPFLAGS for Homebrew OpenSSL

### 4. macOS Gatekeeper Issues
**Error**: `"ken-mcp-server" cannot be opened because the developer cannot be verified`
**Covered**: ❌ Should add
**Solution**: System Preferences > Security & Privacy > Allow

## 🪟 Windows-Specific Errors

### 1. Visual C++ Missing
**Error**: `Microsoft Visual C++ 14.0 or greater is required`
**Covered**: ✅ Yes
**Solution**: Install Build Tools or use pre-compiled wheels

### 2. DLL Load Failed
**Error**: `ImportError: DLL load failed while importing _cffi_backend`
**Covered**: ✅ Yes
**Solution**: Install VC++ Redistributable

### 3. Long Path Issues
**Error**: `FileNotFoundError` with paths > 260 characters
**Covered**: ❌ Should add
**Solution**: Enable long path support in Windows

### 4. WSL vs Windows Python Confusion
**Error**: Mixed path separators or module not found
**Covered**: ✅ Yes
**Solution**: Use consistent Python environment

### 5. Windows Defender Blocking
**Error**: Script execution blocked
**Covered**: ❌ Should add
**Solution**: Add exception or disable real-time protection temporarily

## 🌐 Cross-Platform Errors

### 1. Proxy/Firewall Issues
**Error**: `Failed to establish a new connection`
**Covered**: ✅ Yes
**Solution**: Configure proxy settings

### 2. Pip Version Too Old
**Error**: Various dependency resolution errors
**Covered**: ✅ Yes
**Solution**: Upgrade pip

### 3. Python Version Too Old
**Error**: `SyntaxError` or `ImportError` for modern features
**Covered**: ✅ Yes
**Solution**: Requires Python 3.8+

### 4. Virtual Environment Issues
**Error**: Packages installed but not found
**Covered**: ✅ Yes
**Solution**: Activate virtual environment properly

### 5. PATH Issues
**Error**: `ken-mcp-server: command not found`
**Covered**: ✅ Yes
**Solution**: Add scripts directory to PATH

### 6. Conflicting Package Versions
**Error**: `ImportError: cannot import name X from Y`
**Covered**: ✅ Yes (general solution)
**Solution**: Clean virtual environment

### 7. Missing Dependencies
**Error**: `ModuleNotFoundError: No module named 'typing_extensions'`
**Covered**: ✅ Yes
**Solution**: Install missing package

### 8. Network Timeouts
**Error**: `ReadTimeoutError` during pip install
**Covered**: ✅ Yes
**Solution**: Retry or use different index

## 📦 MCP-Specific Errors

### 1. Port Already in Use
**Error**: `Address already in use`
**Covered**: ✅ Yes
**Solution**: Check what's using the port

### 2. Claude Code Config Issues
**Error**: MCP fails to connect in Claude Code
**Covered**: ✅ Yes
**Solution**: Proper configuration examples provided

### 3. FastMCP Import Errors
**Error**: Various fastmcp-related import errors
**Covered**: ✅ Yes
**Solution**: Specific error messages and fixes

### 4. JSON-RPC Communication Errors
**Error**: `Failed to communicate with MCP server`
**Covered**: ❌ Should add
**Solution**: Check server logs and network

### 5. Tool Registration Failures
**Error**: Tools not appearing in Claude Code
**Covered**: ❌ Should add
**Solution**: Verify tool decorators and server startup

## Summary

**Well Covered** (✅):
- CFFI/Cryptography installation issues
- System dependency errors
- Permission and PATH problems
- Platform-specific build issues
- Proxy and network problems
- Python version compatibility
- Virtual environment issues

**Should Add** (❌):
- GLIBC version issues (older Linux systems)
- macOS Gatekeeper warnings
- Windows long path support
- Windows Defender interference
- JSON-RPC communication debugging
- Tool registration validation
- Server startup validation