#!/usr/bin/env python3
"""Debug MCP server template - add this to the top of your generated server.py"""

import sys
import os
import logging
from datetime import datetime

# Set up logging to file
log_file = f"/tmp/mcp_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"=== MCP Server Starting ===")
logger.info(f"Python: {sys.version}")
logger.info(f"Executable: {sys.executable}")
logger.info(f"Working Dir: {os.getcwd()}")
logger.info(f"Script: {__file__}")
logger.info(f"Log file: {log_file}")

# Log all imports
original_import = __builtins__.__import__
def logging_import(name, *args, **kwargs):
    result = original_import(name, *args, **kwargs)
    if name.startswith(('fastmcp', 'mcp')):
        logger.debug(f"Imported: {name}")
    return result
__builtins__.__import__ = logging_import

# Add this after your FastMCP import
try:
    from fastmcp import FastMCP, Context
    logger.info("✅ FastMCP imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import FastMCP: {e}")
    raise

# Then when creating mcp instance, wrap it:
# mcp = FastMCP(...)  # Your existing code
# logger.info(f"✅ MCP instance created: {mcp}")

# At the very end, modify the main block:
# if __name__ == "__main__":
#     logger.info("Starting MCP server...")
#     try:
#         mcp.run()
#     except Exception as e:
#         logger.error(f"Server crashed: {e}")
#         raise