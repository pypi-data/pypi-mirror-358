#!/bin/bash
# Unix shell script for MCP server
cd "$(dirname "$0")"
python3.11 run_server.py "$@"
