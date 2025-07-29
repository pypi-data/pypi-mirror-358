#!/usr/bin/env python3
"""Test MCP protocol communication"""

import subprocess
import json
import sys
import time

def test_mcp_protocol(server_path):
    """Test if server responds correctly to MCP protocol"""
    print(f"Testing MCP protocol for: {server_path}")
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(1)
    
    # Send a basic JSON-RPC request (initialize)
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {}
        }
    }
    
    try:
        # Send request
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        
        # Wait for response
        time.sleep(1)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Server exited immediately!")
            print(f"Exit code: {process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return
        
        # Try to read response
        import select
        if select.select([process.stdout], [], [], 0.1)[0]:
            response = process.stdout.readline()
            print(f"✅ Got response: {response[:100]}...")
            
            # Check if it's valid JSON
            try:
                json.loads(response)
                print("✅ Response is valid JSON")
            except:
                print("❌ Response is not valid JSON")
                print(f"   This breaks MCP protocol!")
        else:
            print("❌ No response from server")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        process.terminate()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_mcp_protocol(sys.argv[1])
    else:
        print("Usage: python test_mcp_protocol.py <path_to_server.py>")