#!/usr/bin/env python3
"""
Standalone test for text utilities
Can run without fastmcp dependency
"""

import sys
import unittest
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly from the module to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "text_utils", 
    Path(__file__).parent.parent / "ken_mcp" / "utils" / "text.py"
)
text_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(text_utils)

# Import functions
escape_for_docstring = text_utils.escape_for_docstring
clean_requirements = text_utils.clean_requirements
truncate_text = text_utils.truncate_text
sanitize_project_name = text_utils.sanitize_project_name
format_json_string = text_utils.format_json_string
indent_text = text_utils.indent_text


class TestTextUtils(unittest.TestCase):
    """Test text processing utilities"""
    
    # Happy path tests
    def test_escape_for_docstring_normalText_returnsUnchanged(self):
        result = escape_for_docstring("Hello world")
        self.assertEqual(result, "Hello world")
    
    def test_clean_requirements_normalText_returnsClean(self):
        result = clean_requirements("Build a todo app")
        self.assertEqual(result, "Build a todo app")
    
    def test_truncate_text_shortText_returnsUnchanged(self):
        result = truncate_text("Short", 10)
        self.assertEqual(result, "Short")
    
    def test_sanitize_project_name_validName_returnsLowercase(self):
        result = sanitize_project_name("MyProject")
        self.assertEqual(result, "myproject")
    
    def test_format_json_string_dict_returnsJsonString(self):
        result = format_json_string({"key": "value"})
        self.assertEqual(result, '{"key": "value"}')
    
    def test_indent_text_singleLine_indentsCorrectly(self):
        result = indent_text("hello", 4)
        self.assertEqual(result, "    hello")
    
    # Edge cases
    def test_escape_for_docstring_withDoubleQuotes_replacesWithSingle(self):
        result = escape_for_docstring('He said "hello"')
        self.assertEqual(result, "He said 'hello'")
    
    def test_escape_for_docstring_longText_truncatesAt500(self):
        long_text = "a" * 600
        result = escape_for_docstring(long_text)
        self.assertEqual(len(result), 500)
        self.assertTrue(result.endswith("..."))
    
    def test_clean_requirements_withNewlines_removesNewlines(self):
        result = clean_requirements("Build\na\ntodo\napp")
        self.assertEqual(result, "Build a todo app")
    
    def test_sanitize_project_name_specialChars_replacesWithUnderscore(self):
        result = sanitize_project_name("my@project#123")
        self.assertEqual(result, "my_project_123")
    
    def test_indent_text_emptyLines_preservesEmpty(self):
        text = "line1\n\nline3"
        result = indent_text(text, 4)
        expected = "    line1\n\n    line3"
        self.assertEqual(result, expected)
    
    # Error cases
    def test_escape_for_docstring_emptyString_returnsEmpty(self):
        result = escape_for_docstring("")
        self.assertEqual(result, "")
    
    def test_sanitize_project_name_emptyString_returnsEmpty(self):
        result = sanitize_project_name("")
        self.assertEqual(result, "")
    
    def test_format_json_string_none_returnsNull(self):
        result = format_json_string(None)
        self.assertEqual(result, 'null')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)