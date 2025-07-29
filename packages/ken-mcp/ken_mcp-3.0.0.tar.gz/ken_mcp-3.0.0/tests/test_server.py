"""Test the KEN-MCP server entry point"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ken_mcp.server import main


class TestServerEntryPoint:
    """Test the server entry point"""
    
    @patch('ken_mcp.server.mcp')
    def test_main_calls_run(self, mock_mcp):
        """Test that main() calls mcp.run()"""
        # Set up mock
        mock_mcp.run = MagicMock()
        
        # Call main
        main()
        
        # Verify mcp.run was called
        mock_mcp.run.assert_called_once()
    
    def test_server_imports(self):
        """Test that server can be imported without errors"""
        try:
            import ken_mcp.server
            assert hasattr(ken_mcp.server, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import server: {e}")