#!/usr/bin/env python3
"""Test if MCP server stays running or exits immediately"""

import subprocess
import time
import sys

def test_server(server_path):
    """Test if server stays running"""
    print(f"Testing: {server_path}")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, server_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit
    time.sleep(2)
    
    # Check if still running
    poll = process.poll()
    
    if poll is None:
        print("✅ Server is still running after 2 seconds")
        print("   (This is good - it should stay running)")
        process.terminate()
    else:
        print(f"❌ Server exited with code: {poll}")
        stdout, stderr = process.communicate()
        if stdout:
            print(f"STDOUT:\n{stdout}")
        if stderr:
            print(f"STDERR:\n{stderr}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_server(sys.argv[1])
    else:
        print("Usage: python test_server_persistence.py <path_to_server.py>")