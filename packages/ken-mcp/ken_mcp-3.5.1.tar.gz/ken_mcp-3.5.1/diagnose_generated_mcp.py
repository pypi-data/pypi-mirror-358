#!/usr/bin/env python3
"""Diagnose issues with generated MCP servers"""

import sys
import ast
import os

def check_mcp_server(filepath):
    """Check a generated MCP server for common issues"""
    print(f"\n🔍 Checking: {filepath}")
    print("=" * 60)
    
    if not os.path.exists(filepath):
        print("❌ File does not exist!")
        return
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for critical components
    checks = {
        "Has shebang": content.startswith("#!/usr/bin/env python"),
        "Imports FastMCP": "from fastmcp import FastMCP" in content,
        "Creates mcp instance": "mcp = FastMCP(" in content,
        "Has main block": 'if __name__ == "__main__"' in content,
        "Calls mcp.run()": "mcp.run()" in content,
        "Has at least one tool": "@mcp.tool" in content,
    }
    
    for check, result in checks.items():
        print(f"{'✅' if result else '❌'} {check}")
    
    # Check for syntax errors
    try:
        ast.parse(content)
        print("✅ Valid Python syntax")
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
    
    # Check for problematic patterns
    if "TODO: Claude" in content:
        print("⚠️  Contains TODO placeholders - needs implementation")
    
    if "async def" in content and "await" not in content:
        print("⚠️  Has async functions but no await statements")
    
    # Check imports
    print("\n📦 Import statements found:")
    for line in content.split('\n'):
        if line.strip().startswith(('import ', 'from ')):
            print(f"  {line.strip()}")
    
    # Find mcp initialization
    print("\n🔧 MCP initialization:")
    for i, line in enumerate(content.split('\n')):
        if "mcp = FastMCP(" in line:
            # Print this line and next few
            lines = content.split('\n')
            for j in range(i, min(i+10, len(lines))):
                if lines[j].strip():
                    print(f"  {lines[j]}")
                if ")" in lines[j] and j > i:
                    break
    
    # Count tools
    tool_count = content.count("@mcp.tool")
    print(f"\n🛠️  Number of tools defined: {tool_count}")
    
    # Check for common issues in generated code
    if "mcp._tools" in content or "mcp._resources" in content or "mcp._prompts" in content:
        print("❌ Uses private MCP attributes (._tools, ._resources, ._prompts)")
    
    if ".function" in content and "tool.function" in content:
        print("❌ Uses .function instead of .fn for tool access")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_mcp_server(sys.argv[1])
    else:
        print("Usage: python diagnose_generated_mcp.py <path_to_server.py>")
        print("\nExample: python diagnose_generated_mcp.py /path/to/generated-mcp/server.py")