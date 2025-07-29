#!/usr/bin/env python3
"""
Test real-world scenarios
"""

import subprocess
import sys
import os


def test_with_standard_python():
    """Test with system Python (should fail on dependencies)"""
    print("\n1️⃣ Testing with system Python (may lack dependencies):")
    
    # Try with system Python 
    result = subprocess.run(
        ['python3', '-c', 'from ken_mcp.server import main; main()'],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print("Output (first 500 chars):")
        print(result.stdout[:500])
    if result.stderr:
        print("Stderr (first 500 chars):")
        print(result.stderr[:500])
    
    # Check if our error handling works
    if result.returncode != 0:
        if "CFFI backend not properly installed" in result.stdout:
            print("✅ CFFI error message displayed correctly")
        elif "Missing dependency" in result.stdout:
            print("✅ Missing dependency error displayed correctly")
        elif "Failed to import fastmcp" in result.stdout:
            print("✅ Import error displayed correctly")


def test_cli_commands_with_pipx():
    """Test CLI commands with working environment"""
    print("\n2️⃣ Testing CLI commands with pipx Python:")
    
    pipx_python = '/Users/kenkai/.local/pipx/venvs/fastmcp/bin/python3'
    
    # Test verify
    print("\n   Testing 'verify' command:")
    result = subprocess.run(
        [pipx_python, '-m', 'ken_mcp.cli', 'verify'],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    print(f"   Exit code: {result.returncode}")
    if "ken-mcp is ready to use" in result.stdout:
        print("   ✅ Verify command works correctly")
    
    # Test diagnose
    print("\n   Testing 'diagnose' command:")
    result = subprocess.run(
        [pipx_python, '-m', 'ken_mcp.cli', 'diagnose'],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    print(f"   Exit code: {result.returncode}")
    if "System Information" in result.stdout and "MCP-Specific Checks" in result.stdout:
        print("   ✅ Diagnose command works correctly")


def test_install_checker_warnings():
    """Test install checker warnings"""
    print("\n3️⃣ Testing install checker directly:")
    
    test_script = """
import sys
sys.path.insert(0, '.')

from ken_mcp.install_checker import InstallChecker

checker = InstallChecker()

# Force some warnings
checker.system = "Linux"
checker.check_system_deps()

# Check network with no connection
import urllib.request
urllib.request.urlopen = lambda *args, **kwargs: (_ for _ in ()).throw(Exception("No network"))
checker.check_network_connectivity()

# Show results
print("Warnings found:", len(checker.warnings))
for w in checker.warnings:
    print(f"  - {w[:60]}...")
"""
    
    result = subprocess.run(
        [sys.executable, '-c', test_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output:")
    print(result.stdout)


def test_mcp_checker():
    """Test MCP-specific checker"""
    print("\n4️⃣ Testing MCP checker:")
    
    test_script = """
import sys
sys.path.insert(0, '.')

from ken_mcp.mcp_checker import check_claude_code_config, suggest_mcp_config

# Test config check
issues = check_claude_code_config()
print(f"Config issues found: {len(issues)}")

# Test suggestions
print("\\nGenerating config suggestions...")
suggest_mcp_config()
"""
    
    result = subprocess.run(
        [sys.executable, '-c', test_script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("Output (first 400 chars):")
    print(result.stdout[:400])
    
    if "mcpServers" in result.stdout:
        print("✅ MCP config suggestions generated correctly")


if __name__ == "__main__":
    print("🧪 Testing real-world scenarios...")
    print("="*60)
    
    test_with_standard_python()
    test_cli_commands_with_pipx()
    test_install_checker_warnings()
    test_mcp_checker()
    
    print("\n✅ Real-world scenario tests completed!")