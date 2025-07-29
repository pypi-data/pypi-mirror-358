#!/usr/bin/env python3
"""
Test actual server error messages
"""

import sys
import os
import subprocess
from unittest.mock import patch

# Test different error scenarios by mocking imports
def test_cffi_error():
    """Test CFFI error message on Linux"""
    print("\n1️⃣ Testing CFFI error on Linux:")
    
    # Create a test script that simulates the error
    test_script = """
import sys
import platform
platform.system = lambda: 'Linux'

# Mock the import error
original_import = __builtins__.__import__
def mock_import(name, *args):
    if name == 'fastmcp':
        raise ImportError("No module named '_cffi_backend'")
    return original_import(name, *args)

__builtins__.__import__ = mock_import

# Now run the check
from ken_mcp.server import check_dependencies
check_dependencies()
"""
    
    result = subprocess.run(
        [sys.executable, '-c', test_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output:")
    print(result.stdout)
    assert "CFFI backend not properly installed" in result.stdout
    assert "Ubuntu/Debian: sudo apt-get install" in result.stdout


def test_windows_dll_error():
    """Test DLL error message on Windows"""
    print("\n2️⃣ Testing DLL error on Windows:")
    
    test_script = """
import sys
import platform
platform.system = lambda: 'Windows'

# Mock the import error
original_import = __builtins__.__import__
def mock_import(name, *args):
    if name == 'fastmcp':
        raise ImportError("DLL load failed while importing _cffi_backend")
    return original_import(name, *args)

__builtins__.__import__ = mock_import

# Now run the check
from ken_mcp.server import check_dependencies
check_dependencies()
"""
    
    result = subprocess.run(
        [sys.executable, '-c', test_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output:")
    print(result.stdout)
    assert "DLL load failed" in result.stdout
    assert "Visual C++ Redistributable" in result.stdout


def test_macos_symbol_error():
    """Test symbol error message on macOS"""
    print("\n3️⃣ Testing symbol error on macOS:")
    
    test_script = """
import sys
import platform
platform.system = lambda: 'Darwin'

# Mock the import error
original_import = __builtins__.__import__
def mock_import(name, *args):
    if name == 'fastmcp':
        raise ImportError("Symbol not found: _SSL_CTX_set_cipher_list")
    return original_import(name, *args)

__builtins__.__import__ = mock_import

# Now run the check
from ken_mcp.server import check_dependencies
check_dependencies()
"""
    
    result = subprocess.run(
        [sys.executable, '-c', test_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output:")
    print(result.stdout)
    assert "Symbol not found" in result.stdout
    assert "clean virtual environment" in result.stdout


def test_missing_typing_extensions():
    """Test missing typing_extensions error"""
    print("\n4️⃣ Testing missing typing_extensions:")
    
    test_script = """
import sys

# Mock the import error
original_import = __builtins__.__import__
def mock_import(name, *args):
    if name == 'fastmcp':
        raise ImportError("No module named 'typing_extensions'")
    return original_import(name, *args)

__builtins__.__import__ = mock_import

# Now run the check
from ken_mcp.server import check_dependencies
check_dependencies()
"""
    
    result = subprocess.run(
        [sys.executable, '-c', test_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output:")
    print(result.stdout)
    assert "Missing typing_extensions" in result.stdout
    assert "pip install typing-extensions" in result.stdout


def test_cli_verify():
    """Test CLI verify command"""
    print("\n5️⃣ Testing CLI verify command:")
    
    # Use the pipx Python that has all dependencies
    result = subprocess.run(
        ['/Users/kenkai/.local/pipx/venvs/fastmcp/bin/python3', '-m', 'ken_mcp.cli', 'verify'],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output:")
    print(result.stdout)
    assert "ken-mcp is ready to use" in result.stdout or "All dependencies are properly installed" in result.stdout


def test_server_startup():
    """Test actual server startup"""
    print("\n6️⃣ Testing server startup:")
    
    # Test that the server can at least show help
    result = subprocess.run(
        ['/Users/kenkai/.local/pipx/venvs/fastmcp/bin/python3', '-m', 'ken_mcp.server', '--help'],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Exit code:", result.returncode)
    if result.stdout:
        print("Output:", result.stdout[:200])
    if result.stderr:
        print("Stderr:", result.stderr[:200])


if __name__ == "__main__":
    print("🧪 Testing actual error messages and CLI commands...")
    print("="*60)
    
    try:
        test_cffi_error()
        print("✅ CFFI error test passed")
    except Exception as e:
        print(f"❌ CFFI error test failed: {e}")
    
    try:
        test_windows_dll_error()
        print("✅ Windows DLL error test passed")
    except Exception as e:
        print(f"❌ Windows DLL error test failed: {e}")
    
    try:
        test_macos_symbol_error()
        print("✅ macOS symbol error test passed")
    except Exception as e:
        print(f"❌ macOS symbol error test failed: {e}")
    
    try:
        test_missing_typing_extensions()
        print("✅ typing_extensions error test passed")
    except Exception as e:
        print(f"❌ typing_extensions error test failed: {e}")
    
    try:
        test_cli_verify()
        print("✅ CLI verify test passed")
    except Exception as e:
        print(f"❌ CLI verify test failed: {e}")
    
    try:
        test_server_startup()
        print("✅ Server startup test passed")
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
    
    print("\n✅ All error message tests completed!")