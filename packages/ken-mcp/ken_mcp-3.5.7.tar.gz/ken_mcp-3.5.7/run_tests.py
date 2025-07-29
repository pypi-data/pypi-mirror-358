#!/usr/bin/env python3
"""Run the KEN-MCP test suite"""

import subprocess
import sys

def run_tests():
    """Run pytest with coverage"""
    print("🧪 Running KEN-MCP Test Suite...\n")
    
    # Install test dependencies first
    print("📦 Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[test]"])
    
    print("\n🔬 Running tests with coverage...\n")
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "-v",
        "--cov=ken_mcp",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ])
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()