#!/usr/bin/env python3
"""Universal MCP server runner - works on all platforms"""
import sys
import os
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
try:
    from server import mcp
    mcp.run()
except ImportError as e:
    print(f"Error importing server: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error running server: {e}", file=sys.stderr)
    sys.exit(1)
