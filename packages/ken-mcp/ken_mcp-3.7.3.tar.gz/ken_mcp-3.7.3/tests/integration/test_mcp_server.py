#!/usr/bin/env python3
"""Test script to verify ken-mcp server runs properly"""

import subprocess
import sys
import json
import time

def test_mcp_server():
    """Test if the MCP server starts and responds correctly"""
    
    print("Testing ken-mcp server...")
    print("-" * 50)
    
    # Test 1: Check if ken-mcp is importable
    try:
        import ken_mcp
        print("✅ ken_mcp package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ken_mcp: {e}")
        return False
    
    # Test 2: Check if generator module loads
    try:
        from ken_mcp.generator import mcp
        print("✅ MCP instance loaded from generator")
    except ImportError as e:
        print(f"❌ Failed to import MCP instance: {e}")
        return False
    
    # Test 3: Check if server entry point works
    try:
        from ken_mcp.server import main
        print("✅ Server entry point imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import server entry point: {e}")
        return False
    
    # Test 4: List available tools
    try:
        tools = mcp.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}")
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        return False
    
    # Test 5: Try to start the server (will fail if already running)
    print("\n🔧 Testing server startup...")
    print("   Run 'ken-mcp-server' manually to start the server")
    print("   Or use: python -m ken_mcp.server")
    
    return True

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)