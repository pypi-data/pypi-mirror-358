#!/usr/bin/env python3
"""
Standalone test for suggestion utilities
Following CLAUDE.md test naming: test_functionName_condition_expectedResult
"""

import sys
import unittest
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import module directly to avoid dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "suggestions", 
    Path(__file__).parent.parent / "ken_mcp" / "utils" / "suggestions.py"
)
suggestions = importlib.util.module_from_spec(spec)

# Mock the constants to avoid import issues
sys.modules['ken_mcp.templates.constants'] = type(sys)('constants')
sys.modules['ken_mcp.templates.constants'].DOMAIN_KEYWORDS = {
    "cooking": ["recipe", "cook", "ingredient", "meal"],
    "task_management": ["task", "todo", "project", "deadline"],
    "monitoring": ["monitor", "track", "watch", "alert"],
}
sys.modules['ken_mcp.templates.constants'].DEPENDENCY_SUGGESTIONS = {
    "api_http": ["httpx", "requests"],
    "web_scraping": ["beautifulsoup4", "requests", "lxml"],
    "database": ["sqlalchemy", "psycopg2", "pymysql"],
}
sys.modules['ken_mcp.templates.constants'].DEFAULT_TOOL_NAMES = {
    0: {
        "recipe": ["add_recipe", "create_recipe", "save_recipe"],
        "task": ["create_task", "add_todo", "new_task"],
        "monitor": ["start_monitor", "add_monitor", "track_item"],
        "default": ["create_item", "add_entry", "initialize"]
    },
    1: {
        "recipe": ["list_recipes", "search_recipes", "get_recipe"],
        "task": ["list_tasks", "get_tasks", "show_todos"],
        "default": ["list_items", "search_data", "query_items"]
    }
}

# Now load the module
spec.loader.exec_module(suggestions)

# Import functions
extract_key_concepts = suggestions.extract_key_concepts
suggest_tool_names = suggestions.suggest_tool_names
suggest_dependencies = suggestions.suggest_dependencies
categorize_requirement = suggestions.categorize_requirement


class TestSuggestions(unittest.TestCase):
    """Test suggestion utilities - 100% coverage for business logic"""
    
    # extract_key_concepts tests - Happy path
    def test_extract_key_concepts_cookingDomain_returnsCooking(self):
        """Test cooking keywords are detected"""
        result = extract_key_concepts("I want to build a recipe manager")
        self.assertIn("cooking", result)
    
    def test_extract_key_concepts_taskDomain_returnsTaskManagement(self):
        """Test task management keywords are detected"""
        result = extract_key_concepts("Create a todo list application")
        self.assertIn("task management", result)
    
    def test_extract_key_concepts_createAction_returnsCreationOperations(self):
        """Test create action is detected"""
        result = extract_key_concepts("I need to create items")
        self.assertIn("creation operations", result)
    
    def test_extract_key_concepts_searchAction_returnsSearchFunctionality(self):
        """Test search action is detected"""
        result = extract_key_concepts("I want to search for data")
        self.assertIn("search functionality", result)
    
    # extract_key_concepts tests - Edge cases
    def test_extract_key_concepts_multipleDomains_returnsAll(self):
        """Test multiple domains are all detected"""
        result = extract_key_concepts("Build a recipe tracker with task management")
        self.assertIn("cooking", result)
        self.assertIn("task management", result)
    
    def test_extract_key_concepts_noDomain_returnsGeneralPurpose(self):
        """Test no matching domain returns general purpose"""
        result = extract_key_concepts("Build something random")
        self.assertEqual(result, ["general purpose"])
    
    def test_extract_key_concepts_emptyString_returnsGeneralPurpose(self):
        """Test empty string returns general purpose"""
        result = extract_key_concepts("")
        self.assertEqual(result, ["general purpose"])
    
    # suggest_tool_names tests - Happy path
    def test_suggest_tool_names_recipeIndex0_returnsRecipeTools(self):
        """Test recipe tools are suggested for index 0"""
        result = suggest_tool_names("recipe manager", 0)
        self.assertIn("add_recipe", result)
        self.assertIn("create_recipe", result)
    
    def test_suggest_tool_names_taskIndex1_returnsListTools(self):
        """Test task list tools are suggested for index 1"""
        result = suggest_tool_names("task tracker", 1)
        self.assertIn("list_tasks", result)
        self.assertIn("get_tasks", result)
    
    def test_suggest_tool_names_unknownDomain_returnsDefaults(self):
        """Test unknown domain returns default tool names"""
        result = suggest_tool_names("unknown thing", 0)
        self.assertIn("create_item", result)
        self.assertIn("add_entry", result)
    
    # suggest_tool_names tests - Edge cases
    def test_suggest_tool_names_highIndex_returnsGenericNames(self):
        """Test high index returns generic tool names"""
        result = suggest_tool_names("anything", 10)
        self.assertEqual(result, ["tool_11", "operation_11"])
    
    def test_suggest_tool_names_emptyRequirements_returnsDefaults(self):
        """Test empty requirements returns defaults"""
        result = suggest_tool_names("", 0)
        self.assertIn("create_item", result)
    
    # suggest_dependencies tests - Happy path
    def test_suggest_dependencies_apiKeywords_returnsHttpLibs(self):
        """Test API keywords suggest HTTP libraries"""
        result = suggest_dependencies("Build an API client")
        self.assertIn("httpx", result)
        self.assertIn("requests", result)
    
    def test_suggest_dependencies_databaseKeywords_returnsDbLibs(self):
        """Test database keywords suggest DB libraries"""
        result = suggest_dependencies("Connect to SQL database")
        self.assertIn("sqlalchemy", result)
    
    def test_suggest_dependencies_webScraping_returnsScrapingLibs(self):
        """Test web scraping keywords suggest scraping libraries"""
        result = suggest_dependencies("Scrape web pages")
        self.assertIn("beautifulsoup4", result)
        self.assertIn("lxml", result)
    
    # suggest_dependencies tests - Edge cases
    def test_suggest_dependencies_multipleDomains_returnsUniqueDeps(self):
        """Test multiple domains return unique dependencies"""
        result = suggest_dependencies("API to scrape web and store in database")
        # Should have dependencies from all domains
        self.assertIn("httpx", result)
        self.assertIn("beautifulsoup4", result)
        self.assertIn("sqlalchemy", result)
        # But no duplicates
        self.assertEqual(len(result), len(set(result)))
    
    def test_suggest_dependencies_noDomain_returnsEmpty(self):
        """Test no matching keywords returns empty list"""
        result = suggest_dependencies("Build something")
        self.assertEqual(result, [])
    
    # categorize_requirement tests - Happy path
    def test_categorize_requirement_apiKeywords_needsEnvTrue(self):
        """Test API keywords set needs_env to True"""
        result = categorize_requirement("Connect to API with key")
        self.assertTrue(result["needs_env"])
        self.assertTrue(result["needs_api"])
    
    def test_categorize_requirement_authKeywords_needsAuthTrue(self):
        """Test auth keywords set needs_auth to True"""
        result = categorize_requirement("User login with OAuth")
        self.assertTrue(result["needs_auth"])
        self.assertTrue(result["needs_env"])
    
    # categorize_requirement tests - Edge cases
    def test_categorize_requirement_noKeywords_allFalse(self):
        """Test no matching keywords returns all False"""
        result = categorize_requirement("Simple calculator")
        self.assertFalse(result["needs_env"])
        self.assertFalse(result["needs_storage"])
        self.assertFalse(result["needs_api"])
        self.assertFalse(result["needs_async"])
        self.assertFalse(result["needs_auth"])
        self.assertFalse(result["needs_web"])
    
    def test_categorize_requirement_multipleCategories_allTrue(self):
        """Test multiple categories can be True"""
        result = categorize_requirement("Async API with database storage and auth")
        self.assertTrue(result["needs_env"])
        self.assertTrue(result["needs_storage"])
        self.assertTrue(result["needs_api"])
        self.assertTrue(result["needs_async"])
        self.assertTrue(result["needs_auth"])


if __name__ == '__main__':
    unittest.main(verbosity=2)