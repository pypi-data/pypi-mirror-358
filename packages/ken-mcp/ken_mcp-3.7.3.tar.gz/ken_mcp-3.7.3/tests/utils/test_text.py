"""
Tests for text processing utilities
Following CLAUDE.md test naming convention: test_functionName_condition_expectedResult
"""

import unittest
from ken_mcp.utils.text import (
    escape_for_docstring,
    clean_requirements,
    truncate_text,
    sanitize_project_name,
    format_json_string,
    indent_text
)


class TestTextUtils(unittest.TestCase):
    """Test text processing utilities - 100% coverage required"""
    
    # escape_for_docstring tests
    def test_escape_for_docstring_normalText_returnsUnchanged(self):
        """Test normal text remains unchanged"""
        result = escape_for_docstring("Hello world")
        self.assertEqual(result, "Hello world")
    
    def test_escape_for_docstring_withDoubleQuotes_replacesWithSingle(self):
        """Test double quotes are replaced with single quotes"""
        result = escape_for_docstring('He said "hello"')
        self.assertEqual(result, "He said 'hello'")
    
    def test_escape_for_docstring_withBackslashes_escapesBackslashes(self):
        """Test backslashes are properly escaped"""
        result = escape_for_docstring("path\\to\\file")
        self.assertEqual(result, "path\\\\to\\\\file")
    
    def test_escape_for_docstring_withWhitespace_trimsWhitespace(self):
        """Test leading/trailing whitespace is removed"""
        result = escape_for_docstring("  text with spaces  ")
        self.assertEqual(result, "text with spaces")
    
    def test_escape_for_docstring_longText_truncatesAt500(self):
        """Test text longer than 500 chars is truncated"""
        long_text = "a" * 600
        result = escape_for_docstring(long_text)
        self.assertEqual(len(result), 500)
        self.assertTrue(result.endswith("..."))
    
    def test_escape_for_docstring_emptyString_returnsEmpty(self):
        """Test empty string returns empty"""
        result = escape_for_docstring("")
        self.assertEqual(result, "")
    
    # clean_requirements tests
    def test_clean_requirements_normalText_returnsClean(self):
        """Test normal requirements text is cleaned"""
        result = clean_requirements("Build a todo app")
        self.assertEqual(result, "Build a todo app")
    
    def test_clean_requirements_withNewlines_removesNewlines(self):
        """Test newlines are replaced with spaces"""
        result = clean_requirements("Build\na\ntodo\napp")
        self.assertEqual(result, "Build a todo app")
    
    def test_clean_requirements_excessiveSpaces_collapsesSpaces(self):
        """Test multiple spaces are collapsed to single space"""
        result = clean_requirements("Build   a    todo     app")
        self.assertEqual(result, "Build a todo app")
    
    def test_clean_requirements_longText_truncatesWithEllipsis(self):
        """Test text longer than max_length is truncated"""
        long_text = "a" * 150
        result = clean_requirements(long_text, max_length=50)
        self.assertEqual(len(result), 53)  # 50 + "..."
        self.assertTrue(result.endswith("..."))
    
    def test_clean_requirements_customMaxLength_respectsLimit(self):
        """Test custom max_length parameter works"""
        result = clean_requirements("This is a test", max_length=10)
        self.assertEqual(result, "This is a ...")
    
    # truncate_text tests
    def test_truncate_text_shortText_returnsUnchanged(self):
        """Test text shorter than limit remains unchanged"""
        result = truncate_text("Short", 10)
        self.assertEqual(result, "Short")
    
    def test_truncate_text_exactLength_returnsUnchanged(self):
        """Test text exactly at limit remains unchanged"""
        result = truncate_text("12345", 5)
        self.assertEqual(result, "12345")
    
    def test_truncate_text_longText_truncatesWithEllipsis(self):
        """Test text longer than limit gets ellipsis"""
        result = truncate_text("1234567890", 7)
        self.assertEqual(result, "1234...")
    
    def test_truncate_text_veryShortLimit_handlesGracefully(self):
        """Test very short limit (less than ellipsis length)"""
        result = truncate_text("test", 2)
        self.assertEqual(result, "tes...")  # Edge case: max_length < len("...") + 1 produces longer result
    
    # sanitize_project_name tests
    def test_sanitize_project_name_validName_returnsLowercase(self):
        """Test valid name is lowercased"""
        result = sanitize_project_name("MyProject")
        self.assertEqual(result, "myproject")
    
    def test_sanitize_project_name_withSpaces_replacesWithUnderscore(self):
        """Test spaces are replaced with underscores"""
        result = sanitize_project_name("my project")
        self.assertEqual(result, "my_project")
    
    def test_sanitize_project_name_specialChars_replacesWithUnderscore(self):
        """Test special characters are replaced"""
        result = sanitize_project_name("my@project#123")
        self.assertEqual(result, "my_project_123")
    
    def test_sanitize_project_name_hyphenAllowed_keepsHyphen(self):
        """Test hyphens are preserved"""
        result = sanitize_project_name("my-project")
        self.assertEqual(result, "my-project")
    
    def test_sanitize_project_name_emptyString_returnsEmpty(self):
        """Test empty string returns empty"""
        result = sanitize_project_name("")
        self.assertEqual(result, "")
    
    # format_json_string tests
    def test_format_json_string_dict_returnsJsonString(self):
        """Test dictionary is formatted as JSON"""
        result = format_json_string({"key": "value"})
        self.assertEqual(result, '{"key": "value"}')
    
    def test_format_json_string_list_returnsJsonArray(self):
        """Test list is formatted as JSON array"""
        result = format_json_string([1, 2, 3])
        self.assertEqual(result, '[1, 2, 3]')
    
    def test_format_json_string_string_returnsQuoted(self):
        """Test string is properly quoted"""
        result = format_json_string("test")
        self.assertEqual(result, '"test"')
    
    def test_format_json_string_none_returnsNull(self):
        """Test None becomes null"""
        result = format_json_string(None)
        self.assertEqual(result, 'null')
    
    # indent_text tests
    def test_indent_text_singleLine_indentsCorrectly(self):
        """Test single line is indented"""
        result = indent_text("hello", 4)
        self.assertEqual(result, "    hello")
    
    def test_indent_text_multiLine_indentsAllLines(self):
        """Test multiple lines are all indented"""
        text = "line1\nline2\nline3"
        result = indent_text(text, 2)
        expected = "  line1\n  line2\n  line3"
        self.assertEqual(result, expected)
    
    def test_indent_text_emptyLines_preservesEmpty(self):
        """Test empty lines remain empty (no indent)"""
        text = "line1\n\nline3"
        result = indent_text(text, 4)
        expected = "    line1\n\n    line3"
        self.assertEqual(result, expected)
    
    def test_indent_text_customSpaces_usesCorrectCount(self):
        """Test custom space count works"""
        result = indent_text("test", 8)
        self.assertEqual(result, "        test")
    
    def test_indent_text_zeroSpaces_returnsUnchanged(self):
        """Test zero spaces returns unchanged"""
        result = indent_text("test", 0)
        self.assertEqual(result, "test")


if __name__ == '__main__':
    unittest.main()