"""
Cross-platform utilities for Python detection and OS-specific handling
"""

import shutil
import subprocess
import platform
from typing import Optional, List, Dict


class PlatformInfo:
    """Information about the current platform and Python setup"""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.python_commands = self._find_python_commands()
        self.best_python = self._select_best_python()
        self.is_windows = self.os_type == "windows"
        self.is_unix = self.os_type in ["linux", "macos"]
        
    def _detect_os(self) -> str:
        """Detect the operating system type"""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        elif system == "linux":
            # Check if running in WSL
            try:
                with open("/proc/version", "r") as f:
                    if "microsoft" in f.read().lower():
                        return "wsl"
            except (FileNotFoundError, PermissionError):
                pass
            return "linux"
        else:
            return "unknown"
    
    def _find_python_commands(self) -> List[Dict[str, str]]:
        """Find all available Python commands and their versions"""
        commands = []
        
        # Common Python command patterns
        candidates = [
            "python3",      # Most universal
            "python",       # Common on Windows
            "py",          # Windows Python Launcher
            "python3.12",   # Specific versions
            "python3.11",
            "python3.10",
            "python3.9",
            "python3.8",
        ]
        
        for cmd in candidates:
            if shutil.which(cmd):
                version_info = self._get_python_version(cmd)
                if version_info:
                    commands.append({
                        "command": cmd,
                        "version": version_info["version"],
                        "version_info": version_info["version_info"],
                        "executable": shutil.which(cmd)
                    })
        
        return commands
    
    def _get_python_version(self, command: str) -> Optional[Dict[str, str]]:
        """Get version information for a Python command"""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.strip() or result.stderr.strip()
                # Parse "Python 3.10.12" format
                if "Python" in version_line:
                    version = version_line.split()[1]
                    return {
                        "version": version,
                        "version_info": version_line
                    }
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        return None
    
    def _select_best_python(self) -> Optional[str]:
        """Select the best Python command to use"""
        if not self.python_commands:
            return None
        
        # Prioritize by version (3.10+ preferred) and command type
        def score_python(cmd_info):
            cmd = cmd_info["command"]
            version = cmd_info["version"]
            
            try:
                major, minor = map(int, version.split(".")[:2])
            except (ValueError, IndexError):
                return 0
            
            score = 0
            
            # Version score (prefer 3.10+)
            if major == 3 and minor >= 10:
                score += 100
            elif major == 3 and minor >= 8:
                score += 80
            else:
                score += 50
                
            # Command preference
            if cmd == "python3":
                score += 20  # Most universal
            elif cmd.startswith("python3."):
                score += 15  # Specific version
            elif cmd == "python":
                score += 10  # Generic
            elif cmd == "py":
                score += 5   # Windows launcher
            
            return score
        
        best = max(self.python_commands, key=score_python)
        return best["command"]
    
    def get_recommended_command(self, script_path: str) -> str:
        """Get the recommended command to run a script on this platform"""
        if not self.best_python:
            return f"python {script_path}"  # Fallback
            
        if self.is_windows:
            # Windows: prefer explicit python command
            return f"{self.best_python} {script_path}"
        else:
            # Unix: try executable first, fallback to python command
            return f"{script_path}"  # Assumes script is executable
    
    def get_mcp_add_command(self, project_name: str, script_path: str) -> str:
        """Get the complete claude mcp add command for this platform"""
        if self.is_windows:
            # Windows: use python command explicitly
            cmd = f"{self.best_python} {script_path}"
        else:
            # Unix: use executable script path
            cmd = script_path
            
        return f'claude mcp add {project_name} "{cmd}"'
    
    def get_install_command(self) -> str:
        """Get the pip install command for this platform"""
        if not self.best_python:
            return "pip install -r requirements.txt"
            
        return f"{self.best_python} -m pip install -r requirements.txt"
    
    def needs_virtual_env_recommendation(self) -> bool:
        """Check if we should recommend virtual environment setup"""
        # Always recommend venv for cross-platform compatibility
        return True


def detect_platform() -> PlatformInfo:
    """Convenience function to detect platform information"""
    return PlatformInfo()


def get_universal_shebang(python_command: str) -> str:
    """Get the most universal shebang line using detected Python"""
    return f"#!/usr/bin/env {python_command}"


def get_platform_specific_scripts(python_command: str) -> Dict[str, str]:
    """Generate platform-specific script content"""
    scripts = {}
    
    # Universal Python script (works on all platforms)
    scripts["run_server.py"] = f'''{get_universal_shebang(python_command)}
"""Universal MCP server runner - works on all platforms"""
import sys
import os
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
try:
    from server import mcp
    mcp.run()
except ImportError as e:
    print(f"Error importing server: {{e}}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error running server: {{e}}", file=sys.stderr)
    sys.exit(1)
'''
    
    # Windows batch file
    scripts["run_server.bat"] = f'''@echo off
REM Windows batch file for MCP server
cd /d "%~dp0"
{python_command} run_server.py %*
'''
    
    # Unix shell script
    scripts["run_server.sh"] = f'''#!/bin/bash
# Unix shell script for MCP server
cd "$(dirname "$0")"
{python_command} run_server.py "$@"
'''
    
    return scripts


if __name__ == "__main__":
    # Test the platform detection
    info = detect_platform()
    print(f"OS: {info.os_type}")
    print(f"Best Python: {info.best_python}")
    print(f"Available Python commands:")
    for cmd in info.python_commands:
        print(f"  {cmd['command']}: {cmd['version']}")
    print(f"Recommended MCP command: {info.get_mcp_add_command('test', '/path/to/run_server.py')}")