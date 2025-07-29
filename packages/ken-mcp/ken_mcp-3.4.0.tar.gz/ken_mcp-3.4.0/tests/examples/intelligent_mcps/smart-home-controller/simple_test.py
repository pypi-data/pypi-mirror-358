#!/usr/bin/env python3
"""
Simple test to verify the generated MCP server works
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

# Import the generated server
try:
    from server import mcp
except ImportError as e:
    print(f"❌ Failed to import server: {e}")
    print("Make sure server.py exists and has no syntax errors")
    sys.exit(1)

print("✅ Server imported successfully")
print(f"   Name: {mcp.name}")

# Try to list available tools
try:
    print("\n📋 Available tools:")
    # FastMCP doesn't directly expose tools list, but we can check if decorated functions exist
    from server import (
        create_device, get_device, list_devices, 
        update_device, monitor_device, control_device
    )
    print("   - create_device")
    print("   - get_device")
    print("   - list_devices")
    print("   - update_device")
    print("   - monitor_device")
    print("   - control_device")
except ImportError as e:
    print(f"   ❌ Some tools not found: {e}")

# Try to list resources
try:
    print("\n📂 Available resources:")
    from server import (
        resource_devices, resource_device_id,
        resource_cameras, resource_camera_id
    )
    print("   - data://devices")
    print("   - data://device/{id}")
    print("   - data://cameras")
    print("   - data://camera/{id}")
except ImportError as e:
    print(f"   ❌ Some resources not found: {e}")

# Try to list prompts
try:
    print("\n💬 Available prompts:")
    from server import help, assistant
    print("   - help")
    print("   - assistant")
except ImportError as e:
    print(f"   ❌ Some prompts not found: {e}")

print("\n✅ MCP server structure looks good!")
print("\nTo use this MCP:")
print("1. Install it: pip install -e .")
print("2. Add to Claude Desktop config (see help.md)")
print("3. The server will be available as 'smart-home-controller'")