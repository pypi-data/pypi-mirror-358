#!/usr/bin/env python3
"""
MCP-specific checks for ken-mcp
"""

import sys
import os
import json
import platform


def check_claude_code_config():
    """Check if Claude Code is properly configured"""
    issues = []
    
    # Common config file locations
    config_paths = []
    
    if platform.system() == "Windows":
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            config_paths.append(os.path.join(appdata, 'Claude', 'claude_config.json'))
    elif platform.system() == "Darwin":  # macOS
        home = os.path.expanduser('~')
        config_paths.extend([
            os.path.join(home, 'Library', 'Application Support', 'Claude', 'config.json'),
            os.path.join(home, '.claude', 'config.json')
        ])
    else:  # Linux
        home = os.path.expanduser('~')
        config_paths.extend([
            os.path.join(home, '.config', 'claude', 'config.json'),
            os.path.join(home, '.claude', 'config.json')
        ])
    
    # Check if ken-mcp-server is in PATH
    from shutil import which
    if not which('ken-mcp-server'):
        issues.append(
            "ken-mcp-server not found in PATH.\n"
            "Make sure the installation directory is in your PATH."
        )
    
    return issues


def check_mcp_runtime_issues():
    """Check for common MCP runtime issues"""
    issues = []
    
    # Check if port 3000 is available (common MCP port)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 3000))
        if result == 0:
            issues.append(
                "Port 3000 is already in use. This might conflict with MCP servers.\n"
                "Check what's using it: lsof -i :3000 (Linux/macOS) or netstat -ano | findstr :3000 (Windows)"
            )
        sock.close()
    except:
        pass
    
    # Check for conflicting Python installations
    if platform.system() == "Windows":
        # Check for WSL Python vs Windows Python confusion
        if os.path.exists('/mnt/c/'):
            issues.append(
                "WSL detected. Make sure you're not mixing WSL and Windows Python.\n"
                "Use either WSL Python or Windows Python consistently."
            )
    
    return issues


def suggest_mcp_config():
    """Suggest Claude Code configuration"""
    print("\n📋 Suggested Claude Code Configuration:")
    print("Add this to your Claude Code settings:\n")
    
    config = {
        "mcpServers": {
            "ken-mcp": {
                "command": "ken-mcp-server"
            }
        }
    }
    
    print(json.dumps(config, indent=2))
    
    print("\nAlternative configurations:")
    
    # With full path
    print("\n1. With full path (if not in PATH):")
    if platform.system() == "Windows":
        path_example = "C:\\\\Users\\\\YourName\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python311\\\\Scripts\\\\ken-mcp-server.exe"
    else:
        path_example = "/home/username/.local/bin/ken-mcp-server"
    
    config_path = {
        "mcpServers": {
            "ken-mcp": {
                "command": path_example
            }
        }
    }
    print(json.dumps(config_path, indent=2))
    
    # With Python module
    print("\n2. Using Python module directly:")
    config_module = {
        "mcpServers": {
            "ken-mcp": {
                "command": "python",
                "args": ["-m", "ken_mcp.server"]
            }
        }
    }
    print(json.dumps(config_module, indent=2))
    
    # With virtual environment
    print("\n3. With virtual environment:")
    if platform.system() == "Windows":
        venv_path = "C:\\\\path\\\\to\\\\venv\\\\Scripts\\\\ken-mcp-server.exe"
    else:
        venv_path = "/path/to/venv/bin/ken-mcp-server"
    
    config_venv = {
        "mcpServers": {
            "ken-mcp": {
                "command": venv_path
            }
        }
    }
    print(json.dumps(config_venv, indent=2))


def check_mcp_specific():
    """Run MCP-specific checks"""
    print("\n🔌 MCP-Specific Checks:")
    
    # Check Claude Code config
    config_issues = check_claude_code_config()
    if config_issues:
        print("\n⚠️  Configuration issues:")
        for issue in config_issues:
            print(f"   {issue}")
    
    # Check runtime issues
    runtime_issues = check_mcp_runtime_issues()
    if runtime_issues:
        print("\n⚠️  Runtime issues:")
        for issue in runtime_issues:
            print(f"   {issue}")
    
    # Show configuration suggestions
    suggest_mcp_config()
    
    return len(config_issues) + len(runtime_issues) == 0


if __name__ == "__main__":
    check_mcp_specific()