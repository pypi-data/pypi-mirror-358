#!/usr/bin/env python3
"""
Tests for validation utilities
Following CLAUDE.md: test_functionName_condition_expectedResult
"""

import sys
import unittest
from pathlib import Path
import tempfile
import os

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import module directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "validation", 
    Path(__file__).parent.parent / "ken_mcp" / "utils" / "validation.py"
)
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)

# Import functions
validate_project = validation.validate_project
check_python_syntax = validation.check_python_syntax
validate_parameter_count = validation.validate_parameter_count
validate_imports = validation.validate_imports
validate_file_path = validation.validate_file_path
validate_url = validation.validate_url
validate_tool_definition = validation.validate_tool_definition
validate_project_name = validation.validate_project_name


class TestValidation(unittest.TestCase):
    """Test validation utilities - 100% coverage for business logic"""
    
    def setUp(self):
        """Create temporary directory for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test_project"
        self.project_path.mkdir()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    # validate_project tests - Happy path
    def test_validate_project_allFilesPresent_returnsValid(self):
        """Test project with all required files is valid"""
        # Create all required files
        required_files = ["server.py", "README.md", "help.md", "test.py", "requirements.txt", ".gitignore", "diagnose.py"]
        for file in required_files:
            (self.project_path / file).write_text("# Test content")
        
        result = validate_project(self.project_path)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["issues"]), 0)
        self.assertEqual(result["files_checked"], 7)
    
    def test_validate_project_validPythonSyntax_noIssues(self):
        """Test valid Python syntax passes validation"""
        (self.project_path / "server.py").write_text("print('Hello')")
        (self.project_path / "test.py").write_text("import unittest")
        # Create other required files
        for file in ["README.md", "help.md", "requirements.txt", ".gitignore", "diagnose.py"]:
            (self.project_path / file).write_text("# Test")
        
        result = validate_project(self.project_path)
        self.assertTrue(result["valid"])
    
    # validate_project tests - Edge cases
    def test_validate_project_missingFiles_returnsInvalid(self):
        """Test missing required files makes project invalid"""
        # Only create some files
        (self.project_path / "server.py").write_text("print('test')")
        (self.project_path / "README.md").write_text("# README")
        
        result = validate_project(self.project_path)
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["issues"]), 0)
        # Should report missing files
        self.assertTrue(any("Missing required file" in issue for issue in result["issues"]))
    
    def test_validate_project_syntaxError_returnsInvalid(self):
        """Test Python syntax error is detected"""
        # Create file with syntax error
        (self.project_path / "server.py").write_text("print('unclosed")
        # Create other files
        for file in ["README.md", "help.md", "test.py", "requirements.txt", ".gitignore", "diagnose.py"]:
            (self.project_path / file).write_text("# Test")
        
        result = validate_project(self.project_path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("Syntax error" in issue for issue in result["issues"]))
    
    # check_python_syntax tests - Happy path
    def test_check_python_syntax_validCode_returnsNone(self):
        """Test valid Python code returns None"""
        test_file = self.project_path / "valid.py"
        test_file.write_text("def hello():\n    return 'world'")
        
        result = check_python_syntax(test_file)
        self.assertIsNone(result)
    
    # check_python_syntax tests - Error cases
    def test_check_python_syntax_syntaxError_returnsErrorMessage(self):
        """Test syntax error returns error message"""
        test_file = self.project_path / "invalid.py"
        test_file.write_text("def hello(\n    return 'world'")
        
        result = check_python_syntax(test_file)
        self.assertIsNotNone(result)
        self.assertIn("Line", result)
    
    def test_check_python_syntax_fileNotFound_returnsError(self):
        """Test non-existent file returns error"""
        result = check_python_syntax(Path("/nonexistent/file.py"))
        self.assertIsNotNone(result)
    
    # validate_parameter_count tests - Happy path
    def test_validate_parameter_count_underLimit_returnsNone(self):
        """Test parameter count under limit returns None"""
        params = [
            {"name": "param1"},
            {"name": "param2"},
            {"name": "param3"}
        ]
        result = validate_parameter_count(params, max_params=4)
        self.assertIsNone(result)
    
    def test_validate_parameter_count_ctxExcluded_returnsNone(self):
        """Test ctx parameter is not counted"""
        params = [
            {"name": "ctx"},
            {"name": "param1"},
            {"name": "param2"},
            {"name": "param3"},
            {"name": "param4"}
        ]
        result = validate_parameter_count(params, max_params=4)
        self.assertIsNone(result)
    
    # validate_parameter_count tests - Error cases
    def test_validate_parameter_count_overLimit_returnsError(self):
        """Test too many parameters returns error"""
        params = [
            {"name": "param1"},
            {"name": "param2"},
            {"name": "param3"},
            {"name": "param4"},
            {"name": "param5"}
        ]
        result = validate_parameter_count(params, max_params=4)
        self.assertIsNotNone(result)
        self.assertIn("Too many parameters", result)
    
    # validate_imports tests - Happy path
    def test_validate_imports_stdlibImports_categorizedCorrectly(self):
        """Test stdlib imports are categorized correctly"""
        imports = [
            "import os",
            "import json",
            "from pathlib import Path",
            "import requests"
        ]
        stdlib = {"os", "json", "pathlib"}
        
        result = validate_imports(imports, stdlib)
        self.assertEqual(len(result["stdlib"]), 3)
        self.assertEqual(len(result["external"]), 1)
        self.assertIn("import requests", result["external"])
    
    # validate_file_path tests - Happy path
    def test_validate_file_path_normalPath_returnsTrue(self):
        """Test normal file path is valid"""
        self.assertTrue(validate_file_path("test/file.txt"))
        self.assertTrue(validate_file_path("my_project/src/main.py"))
    
    # validate_file_path tests - Error cases
    def test_validate_file_path_pathTraversal_returnsFalse(self):
        """Test path traversal attempt returns False"""
        self.assertFalse(validate_file_path("../../../etc/passwd"))
        self.assertFalse(validate_file_path("test/../../../secret"))
    
    def test_validate_file_path_absolutePath_returnsFalse(self):
        """Test absolute path returns False"""
        self.assertFalse(validate_file_path("/etc/passwd"))
        self.assertFalse(validate_file_path("/usr/bin/python"))
    
    # validate_url tests - Happy path
    def test_validate_url_httpUrl_returnsTrue(self):
        """Test HTTP URL is valid"""
        self.assertTrue(validate_url("http://example.com"))
        self.assertTrue(validate_url("https://api.example.com/v1"))
    
    # validate_url tests - Error cases
    def test_validate_url_invalidProtocol_returnsFalse(self):
        """Test invalid protocol returns False"""
        self.assertFalse(validate_url("ftp://example.com"))
        self.assertFalse(validate_url("file:///etc/passwd"))
        self.assertFalse(validate_url("example.com"))
    
    # validate_tool_definition tests - Happy path
    def test_validate_tool_definition_validTool_returnsEmpty(self):
        """Test valid tool definition returns no errors"""
        tool = {
            "name": "my_tool",
            "description": "A test tool",
            "parameters": [
                {"name": "param1", "type": "str"},
                {"name": "param2", "type": "int"}
            ]
        }
        errors = validate_tool_definition(tool)
        self.assertEqual(len(errors), 0)
    
    # validate_tool_definition tests - Error cases
    def test_validate_tool_definition_missingName_returnsError(self):
        """Test missing name returns error"""
        tool = {"description": "A tool"}
        errors = validate_tool_definition(tool)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("missing 'name'" in e for e in errors))
    
    def test_validate_tool_definition_invalidParameters_returnsErrors(self):
        """Test invalid parameters return errors"""
        tool = {
            "name": "my_tool",
            "description": "A tool",
            "parameters": [
                {"type": "str"},  # Missing name
                {"name": "param2"}  # Missing type
            ]
        }
        errors = validate_tool_definition(tool)
        self.assertGreater(len(errors), 1)
    
    # validate_project_name tests - Happy path
    def test_validate_project_name_validName_returnsNone(self):
        """Test valid project name returns None"""
        self.assertIsNone(validate_project_name("my-project"))
        self.assertIsNone(validate_project_name("test_app_123"))
        self.assertIsNone(validate_project_name("MyProject"))
    
    # validate_project_name tests - Error cases
    def test_validate_project_name_empty_returnsError(self):
        """Test empty name returns error"""
        error = validate_project_name("")
        self.assertIsNotNone(error)
        self.assertIn("empty", error)
    
    def test_validate_project_name_tooLong_returnsError(self):
        """Test name over 50 chars returns error"""
        long_name = "a" * 51
        error = validate_project_name(long_name)
        self.assertIsNotNone(error)
        self.assertIn("too long", error)
    
    def test_validate_project_name_invalidChars_returnsError(self):
        """Test invalid characters return error"""
        error = validate_project_name("my@project#")
        self.assertIsNotNone(error)
        self.assertIn("letters, numbers, hyphens, and underscores", error)


if __name__ == '__main__':
    unittest.main(verbosity=2)