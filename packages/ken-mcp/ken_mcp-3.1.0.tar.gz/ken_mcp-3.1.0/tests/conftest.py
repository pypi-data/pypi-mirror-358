"""Pytest configuration and shared fixtures for KEN-MCP tests"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from typing import AsyncGenerator, Generator
from ken_mcp.generator import mcp, Context


class MockContext:
    """Mock context for testing MCP operations"""
    def __init__(self):
        self.messages = []
        self.progress = []
        
    async def info(self, message: str):
        self.messages.append(("info", message))
        
    async def report_progress(self, current: int, total: int, message: str):
        self.progress.append((current, total, message))
        

@pytest.fixture
def mock_context():
    """Provide a mock context for tests"""
    return MockContext()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_plan():
    """Provide a sample plan for testing"""
    return {
        'description': 'Test MCP Server',
        'original_requirements': 'A test MCP server for unit testing',
        'tools': [
            {
                'name': 'test_tool',
                'description': 'A test tool',
                'parameters': [
                    {'name': 'input', 'type': 'str', 'description': 'Test input'}
                ],
                'implementation': 'boilerplate'
            }
        ],
        'resources': [],
        'prompts': [],
        'dependencies': ['fastmcp']
    }


@pytest.fixture
def complex_plan():
    """Provide a complex plan with multiple tools, resources, and prompts"""
    return {
        'description': 'Complex MCP Server with multiple features',
        'original_requirements': 'A complex MCP with file processing, API calls, and data storage',
        'tools': [
            {
                'name': 'process_file',
                'description': 'Process a file with unicode support',
                'parameters': [
                    {'name': 'file_path', 'type': 'str', 'description': 'Path to file'},
                    {'name': 'encoding', 'type': 'Optional[str]', 'description': 'File encoding', 'default': 'utf-8'}
                ],
                'implementation': 'boilerplate'
            },
            {
                'name': 'api_request',
                'description': 'Make an API request',
                'parameters': [
                    {'name': 'url', 'type': 'str', 'description': 'API endpoint'},
                    {'name': 'method', 'type': 'str', 'description': 'HTTP method', 'default': 'GET'},
                    {'name': 'headers', 'type': 'Optional[Dict[str, str]]', 'description': 'Request headers', 'default': None}
                ],
                'implementation': 'boilerplate'
            }
        ],
        'resources': [
            {
                'uri_pattern': 'data://files',
                'description': 'List of processed files',
                'implementation': 'boilerplate'
            }
        ],
        'prompts': [
            {
                'name': 'help',
                'description': 'Get help on using the MCP',
                'implementation': 'boilerplate'
            }
        ],
        'dependencies': ['fastmcp', 'httpx', 'pathlib']
    }


@pytest.mark.asyncio
class AsyncTest:
    """Base class for async tests"""
    pass