"""
KEN-MCP Server Entry Point
This file provides the main entry point for the KEN-MCP server package.
"""

def main():
    """Main entry point for ken-mcp-server command"""
    from ken_mcp.generator import mcp
    mcp.run()

if __name__ == "__main__":
    main()