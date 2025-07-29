"""Unit tests for KEN-MCP generator functions"""

import pytest
from pathlib import Path
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ken_mcp.generator import (
    _escape_for_docstring,
    _suggest_dependencies,
    _generate_test_value,
    _generate_invalid_value,
    _create_project_structure,
    _generate_server_code,
    _generate_documentation,
    _generate_test_file,
    _validate_project,
    generate_mcp_server,
    analyze_requirements
)


class TestEscapeForDocstring:
    """Test the docstring escaping function"""
    
    def test_escape_triple_quotes(self):
        """Test escaping triple quotes"""
        input_str = 'This has """triple quotes""" in it'
        expected = "This has '''triple quotes''' in it"
        assert _escape_for_docstring(input_str) == expected
    
    def test_escape_backslashes(self):
        """Test escaping backslashes"""
        input_str = r"Path with \backslash and \\double"
        expected = r"Path with \\backslash and \\\\double"
        assert _escape_for_docstring(input_str) == expected
    
    def test_escape_complex(self):
        """Test complex escaping scenario"""
        input_str = r'Complex """string""" with \n newline and \\path'
        expected = r"Complex '''string''' with \\n newline and \\\\path"
        assert _escape_for_docstring(input_str) == expected
    
    def test_empty_string(self):
        """Test empty string handling"""
        assert _escape_for_docstring("") == ""


class TestSuggestDependencies:
    """Test dependency suggestion function"""
    
    def test_api_dependencies(self):
        """Test API-related dependencies"""
        requirements = "Create an MCP that makes HTTP requests to REST APIs"
        deps = _suggest_dependencies(requirements)
        assert "httpx" in deps
        assert "requests" in deps
    
    def test_database_dependencies(self):
        """Test database-related dependencies"""
        requirements = "Build an MCP for PostgreSQL database operations"
        deps = _suggest_dependencies(requirements)
        assert "sqlalchemy" in deps
        assert "psycopg2" in deps
    
    def test_file_processing_dependencies(self):
        """Test file processing dependencies"""
        requirements = "Create MCP for processing CSV and Excel files with pandas"
        deps = _suggest_dependencies(requirements)
        assert "pandas" in deps
        assert "openpyxl" in deps
    
    def test_ml_dependencies(self):
        """Test ML/AI dependencies"""
        requirements = "Build an MCP for machine learning predictions and classification"
        deps = _suggest_dependencies(requirements)
        assert "scikit-learn" in deps
        assert "numpy" in deps
    
    def test_no_duplicates(self):
        """Test that dependencies are not duplicated"""
        requirements = "API calls, APIs, REST API, HTTP requests"
        deps = _suggest_dependencies(requirements)
        # Check no duplicates
        assert len(deps) == len(set(deps))


class TestGenerateTestValue:
    """Test the test value generation function"""
    
    def test_file_path_param(self):
        """Test file path parameter detection"""
        assert _generate_test_value("file_path", "str", "") == '"/tmp/test_file.txt"'
        assert _generate_test_value("input_file", "str", "") == '"/tmp/test_file.txt"'
    
    def test_url_param(self):
        """Test URL parameter detection"""
        assert _generate_test_value("url", "str", "") == '"https://example.com/api"'
        assert _generate_test_value("endpoint", "str", "") == '"https://example.com/api"'
    
    def test_email_param(self):
        """Test email parameter detection"""
        assert _generate_test_value("email", "str", "") == '"test@example.com"'
        assert _generate_test_value("user_email", "str", "") == '"test@example.com"'
    
    def test_type_based_values(self):
        """Test type-based value generation"""
        assert _generate_test_value("count", "int", "") == "42"
        assert _generate_test_value("ratio", "float", "") == "3.14"
        assert _generate_test_value("enabled", "bool", "") == "True"
        assert _generate_test_value("items", "list", "") == '["item1", "item2"]'
        assert _generate_test_value("config", "dict", "") == '{"key": "value"}'


class TestGenerateInvalidValue:
    """Test invalid value generation for type testing"""
    
    def test_invalid_for_types(self):
        """Test invalid values for different types"""
        assert _generate_invalid_value("str") == "123"
        assert _generate_invalid_value("int") == '"not_a_number"'
        assert _generate_invalid_value("float") == '"not_a_float"'
        assert _generate_invalid_value("bool") == '"not_a_bool"'
        assert _generate_invalid_value("list") == '"not_a_list"'
        assert _generate_invalid_value("dict") == '"not_a_dict"'
    
    def test_unknown_type(self):
        """Test unknown type returns None"""
        assert _generate_invalid_value("CustomType") is None


@pytest.mark.asyncio
class TestProjectGeneration:
    """Test project generation functions"""
    
    async def test_create_project_structure(self, mock_context, temp_dir):
        """Test project structure creation"""
        project_name = "test-mcp"
        project_path = await _create_project_structure(project_name, str(temp_dir), mock_context)
        
        # Check project was created
        assert project_path.exists()
        assert project_path.name == project_name
        
        # Check required files
        assert (project_path / ".gitignore").exists()
        assert (project_path / ".env.example").exists()
        assert (project_path / "__init__.py").exists()
        
        # Check context messages
        assert any("Creating project structure" in msg for _, msg in mock_context.messages)
    
    async def test_generate_server_code(self, mock_context, temp_dir, sample_plan):
        """Test server code generation"""
        project_path = temp_dir / "test-mcp"
        project_path.mkdir()
        
        await _generate_server_code(project_path, sample_plan, mock_context, "3.10", None)
        
        # Check files were created
        assert (project_path / "server.py").exists()
        assert (project_path / "pyproject.toml").exists()
        
        # Check server.py content
        server_content = (project_path / "server.py").read_text()
        assert "#!/usr/bin/env python3" in server_content
        assert "from fastmcp import FastMCP" in server_content
        assert "@mcp.tool" in server_content
        assert "test_tool" in server_content
        
        # Check pyproject.toml
        pyproject_content = (project_path / "pyproject.toml").read_text()
        assert "test-mcp" in pyproject_content
        assert "fastmcp" in pyproject_content
    
    async def test_generate_documentation(self, mock_context, temp_dir, sample_plan):
        """Test documentation generation"""
        project_path = temp_dir / "test-mcp"
        project_path.mkdir()
        
        await _generate_documentation(project_path, sample_plan, "test-mcp", mock_context, "3.10")
        
        # Check files were created
        assert (project_path / "README.md").exists()
        assert (project_path / "help.md").exists()
        
        # Check README content
        readme_content = (project_path / "README.md").read_text()
        assert "test-mcp" in readme_content
        assert "help.md" in readme_content
        
        # Check help.md content
        help_content = (project_path / "help.md").read_text()
        assert "claude mcp add" in help_content
        assert "Troubleshooting" in help_content
        assert "python3 test.py" in help_content
    
    async def test_generate_test_file(self, mock_context, temp_dir, complex_plan):
        """Test test file generation"""
        project_path = temp_dir / "test-mcp"
        project_path.mkdir()
        
        await _generate_test_file(project_path, complex_plan, "test-mcp", mock_context)
        
        # Check test.py was created
        assert (project_path / "test.py").exists()
        
        # Check test content
        test_content = (project_path / "test.py").read_text()
        assert "#!/usr/bin/env python3" in test_content
        assert "test_process_file" in test_content
        assert "test_api_request" in test_content
        assert "test_resources" in test_content
        assert "test_prompts" in test_content
        assert "MockContext" in test_content
        assert "run_all_tests" in test_content
        
        # Check test has proper structure
        assert "file_path=" in test_content  # Parameter test
        assert '"not_a_number"' in test_content  # Invalid type test
    
    async def test_validate_project(self, mock_context, temp_dir):
        """Test project validation"""
        project_path = temp_dir / "test-mcp"
        project_path.mkdir()
        
        # Create required files
        (project_path / "server.py").write_text("#!/usr/bin/env python3\nmcp = None")
        (project_path / "README.md").write_text("# Test")
        (project_path / "help.md").write_text("# Help")
        (project_path / "test.py").write_text("#!/usr/bin/env python3")
        (project_path / "pyproject.toml").write_text("[project]\nname='test'")
        (project_path / ".gitignore").write_text("*.pyc")
        
        result = await _validate_project(project_path, mock_context)
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["files_checked"] == 6
    
    async def test_validate_project_missing_files(self, mock_context, temp_dir):
        """Test project validation with missing files"""
        project_path = temp_dir / "test-mcp"
        project_path.mkdir()
        
        # Only create some files
        (project_path / "server.py").write_text("#!/usr/bin/env python3")
        
        result = await _validate_project(project_path, mock_context)
        
        assert result["valid"] is False
        assert len(result["issues"]) > 0
        assert "Missing required file: README.md" in result["issues"]


@pytest.mark.asyncio
class TestMainTools:
    """Test the main MCP tools"""
    
    async def test_analyze_requirements(self, mock_context):
        """Test requirements analysis"""
        requirements = "Create a calculator MCP that can add and subtract"
        result = await analyze_requirements(mock_context, requirements)
        
        assert "description" in result
        assert "suggested_tools" in result
        assert result["suggested_tools"] > 0
        assert "dependencies" in result
    
    async def test_generate_mcp_server_basic(self, mock_context, temp_dir):
        """Test basic MCP server generation"""
        result = await generate_mcp_server(
            ctx=mock_context,
            requirements="Create a simple calculator MCP",
            project_name="calc-mcp",
            output_dir=str(temp_dir),
            include_resources=False,
            include_prompts=False
        )
        
        assert result["success"] is True
        assert result["project_path"] == str(temp_dir / "calc-mcp")
        assert result["tools_generated"] >= 3  # Default tools
        
        # Check files exist
        project_path = Path(result["project_path"])
        assert (project_path / "server.py").exists()
        assert (project_path / "test.py").exists()
        assert (project_path / "help.md").exists()
    
    async def test_edge_case_requirements(self, mock_context, temp_dir):
        """Test with edge case requirements"""
        # Test with backslashes and quotes
        requirements = r'Build MCP with "special" chars and \backslash paths'
        result = await generate_mcp_server(
            ctx=mock_context,
            requirements=requirements,
            project_name="edge-case-mcp",
            output_dir=str(temp_dir)
        )
        
        assert result["success"] is True
        
        # Check generated files don't have syntax errors
        project_path = Path(result["project_path"])
        server_content = (project_path / "server.py").read_text()
        
        # Try to parse as Python (will raise SyntaxError if invalid)
        import ast
        ast.parse(server_content)