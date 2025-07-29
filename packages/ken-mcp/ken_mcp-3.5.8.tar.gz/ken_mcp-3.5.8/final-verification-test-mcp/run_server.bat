@echo off
REM Windows batch file for MCP server
cd /d "%~dp0"
python3.11 run_server.py %*
