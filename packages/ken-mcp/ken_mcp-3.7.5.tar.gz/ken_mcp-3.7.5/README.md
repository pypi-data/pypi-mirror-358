# KEN-MCP - Universal MCP Server Generator

Generate complete MCP (Model Context Protocol) servers from natural language descriptions.

## Features

- **Natural Language to MCP**: Describe what you want, get a working MCP server
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Smart Analysis**: Understands your requirements and generates appropriate tools
- **Complete Package**: Generates server code, tests, documentation, and setup scripts
- **FastMCP Integration**: Built on the reliable FastMCP framework

## Installation

```bash
pip install ken-mcp
```

## Quick Start

```python
from ken_mcp import mcp_ken

# Generate an MCP server
result = await mcp_ken.generate(
    "I want an MCP that helps me manage my todo list with categories and priorities"
)
```

## Generated MCP Structure

Each generated MCP includes:
- **server.py**: Main MCP server implementation
- **run_server.py**: Universal runner script
- **test.py**: Comprehensive test suite
- **verify.py**: Implementation verification
- **diagnose.py**: Cross-platform diagnostic tool
- **README.md**: Project documentation
- **help.md**: Setup and troubleshooting guide

## Documentation

- See individual MCP folders for specific documentation
- Each MCP includes comprehensive help.md for setup instructions
- Run diagnostic scripts for troubleshooting

## License

MIT License - see LICENSE file for details