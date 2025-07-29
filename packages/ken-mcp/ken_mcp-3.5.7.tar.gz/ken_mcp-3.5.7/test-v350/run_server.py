#!/usr/bin/env python3.10
"""Wrapper script to run the MCP server with clean stdout"""
import sys
import os

# Suppress deprecation warnings before importing
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from server import mcp
mcp.run()
