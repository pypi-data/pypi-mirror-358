#!/usr/bin/env python3
"""
Tests for requirements analyzer
Following CLAUDE.md: test_functionName_condition_expectedResult
"""

import sys
import unittest
from pathlib import Path
import importlib.util

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock dependencies first
sys.modules['ken_mcp.templates.constants'] = type(sys)('constants')
sys.modules['ken_mcp.utils.text'] = type(sys)('text')
sys.modules['ken_mcp.utils.suggestions'] = type(sys)('suggestions')

# Mock functions
def mock_clean_requirements(text, max_length=100):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def mock_suggest_tool_names(requirements, index):
    if "recipe" in requirements.lower() and index == 0:
        return ["add_recipe", "create_recipe"]
    elif "task" in requirements.lower() and index == 1:
        return ["list_tasks", "get_tasks"]
    elif index == 1:
        return ["tool_two"]
    elif index == 2:
        return ["tool_three"]
    return ["tool_one"]

def mock_suggest_resource_uris(requirements):
    if "list" in requirements.lower():
        return [{"uri_pattern": "data://items", "description": "Collection of items"}]
    return []

def mock_suggest_prompt_names(requirements):
    if "help" in requirements.lower():
        return [{"name": "help", "description": "Get help"}]
    return []

sys.modules['ken_mcp.utils.text'].clean_requirements = mock_clean_requirements
sys.modules['ken_mcp.utils.suggestions'].suggest_tool_names = mock_suggest_tool_names
sys.modules['ken_mcp.utils.suggestions'].suggest_resource_uris = mock_suggest_resource_uris
sys.modules['ken_mcp.utils.suggestions'].suggest_prompt_names = mock_suggest_prompt_names

# Import models module directly first
models_spec = importlib.util.spec_from_file_location(
    "models", 
    Path(__file__).parent.parent / "ken_mcp" / "core" / "models.py"
)
models = importlib.util.module_from_spec(models_spec)
models_spec.loader.exec_module(models)

# Make models available to analyzer
sys.modules['ken_mcp.core.models'] = models

# Now import analyzer
spec = importlib.util.spec_from_file_location(
    "analyzer", 
    Path(__file__).parent.parent / "ken_mcp" / "core" / "analyzer.py"
)
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)

# Import functions
analyze_and_plan = analyzer.analyze_and_plan
generate_placeholder_tools = analyzer.generate_placeholder_tools
generate_placeholder_resources = analyzer.generate_placeholder_resources
generate_placeholder_prompts = analyzer.generate_placeholder_prompts


class TestAnalyzer(unittest.TestCase):
    """Test requirements analyzer - 100% coverage for business logic"""
    
    # analyze_and_plan tests - Happy path
    def test_analyze_and_plan_basicRequirements_returnsValidPlan(self):
        """Test basic requirements return valid plan"""
        plan = analyze_and_plan("Build a todo app")
        
        self.assertEqual(plan.description, "MCP server for: Build a todo app")
        self.assertEqual(plan.original_requirements, "Build a todo app")
        self.assertEqual(len(plan.tools), 3)  # Default 3 tools
        self.assertEqual(len(plan.dependencies), 3)  # pathlib, json, typing
    
    def test_analyze_and_plan_withResources_includesResources(self):
        """Test plan includes resources when requested"""
        plan = analyze_and_plan("Build a list manager", include_resources=True)
        
        self.assertGreater(len(plan.resources), 0)
        # Should include suggested resource from mock
        self.assertTrue(any(r.uri_pattern == "data://items" for r in plan.resources))
    
    def test_analyze_and_plan_withPrompts_includesPrompts(self):
        """Test plan includes prompts when requested"""
        plan = analyze_and_plan("Build app with help", include_prompts=True)
        
        self.assertGreater(len(plan.prompts), 0)
        # Should include help prompt
        self.assertTrue(any(p.name == "help" for p in plan.prompts))
    
    # analyze_and_plan tests - Edge cases
    def test_analyze_and_plan_noResources_excludesResources(self):
        """Test plan excludes resources when not requested"""
        plan = analyze_and_plan("Build app", include_resources=False)
        
        self.assertEqual(len(plan.resources), 0)
    
    def test_analyze_and_plan_noPrompts_excludesPrompts(self):
        """Test plan excludes prompts when not requested"""
        plan = analyze_and_plan("Build app", include_prompts=False)
        
        self.assertEqual(len(plan.prompts), 0)
    
    def test_analyze_and_plan_longRequirements_truncatesDescription(self):
        """Test long requirements are truncated in description"""
        long_req = "a" * 150
        plan = analyze_and_plan(long_req)
        
        # Description should be truncated
        self.assertTrue(plan.description.endswith("..."))
        # But original requirements preserved
        self.assertEqual(plan.original_requirements, long_req)
    
    # generate_placeholder_tools tests
    def test_generate_placeholder_tools_recipeRequirements_suggestsRecipeTools(self):
        """Test recipe requirements suggest recipe-specific tools"""
        tools = generate_placeholder_tools("Build a recipe manager")
        
        self.assertEqual(len(tools), 3)
        # First tool should have recipe suggestions
        self.assertIn("recipe", tools[0].name)
        self.assertIn("recipe manager", tools[0].description)
    
    def test_generate_placeholder_tools_taskRequirements_suggestsTaskTools(self):
        """Test task requirements suggest task-specific tools"""
        tools = generate_placeholder_tools("Create a task tracker")
        
        # Second tool should have task list suggestions
        self.assertIn("task", tools[1].name)
    
    def test_generate_placeholder_tools_genericRequirements_usesDefaults(self):
        """Test generic requirements use default tool names"""
        tools = generate_placeholder_tools("Build something")
        
        self.assertEqual(tools[0].name, "tool_one")
        self.assertEqual(tools[1].name, "tool_two")
        self.assertEqual(tools[2].name, "tool_three")
    
    def test_generate_placeholder_tools_allTools_haveParameters(self):
        """Test all generated tools have appropriate parameters"""
        tools = generate_placeholder_tools("Build app")
        
        # Tool 1 should have input_data and options
        self.assertEqual(len(tools[0].parameters), 2)
        self.assertEqual(tools[0].parameters[0].name, "input_data")
        self.assertFalse(tools[0].parameters[1].required)  # options is optional
        
        # Tool 2 should have param1 and param2
        self.assertEqual(len(tools[1].parameters), 2)
        self.assertFalse(tools[1].parameters[1].required)  # param2 is optional
        
        # Tool 3 should have data parameter
        self.assertEqual(len(tools[2].parameters), 1)
        self.assertEqual(tools[2].parameters[0].name, "data")
    
    # generate_placeholder_resources tests
    def test_generate_placeholder_resources_withSuggestions_usesSuggestions(self):
        """Test resources use suggestions when available"""
        resources = generate_placeholder_resources("Build a list manager")
        
        # Should use suggested resource
        self.assertTrue(any(r.uri_pattern == "data://items" for r in resources))
        self.assertEqual(len(resources), 1)  # Only suggested, limited to 3
    
    def test_generate_placeholder_resources_noSuggestions_usesDefaults(self):
        """Test resources use defaults when no suggestions"""
        resources = generate_placeholder_resources("Build something")
        
        self.assertEqual(len(resources), 3)
        # Check default resources
        self.assertTrue(any(r.uri_pattern == "data://items" for r in resources))
        self.assertTrue(any(r.uri_pattern == "resource://config" for r in resources))
        self.assertTrue(any(r.uri_pattern == "data://status" for r in resources))
    
    # generate_placeholder_prompts tests
    def test_generate_placeholder_prompts_withSuggestions_usesSuggestions(self):
        """Test prompts use suggestions when available"""
        prompts = generate_placeholder_prompts("Add help system")
        
        # Should have help prompt from suggestion
        self.assertTrue(any(p.name == "help" for p in prompts))
        self.assertEqual(len(prompts), 1)
    
    def test_generate_placeholder_prompts_noSuggestions_usesDefaults(self):
        """Test prompts use defaults when no suggestions"""
        prompts = generate_placeholder_prompts("Build something")
        
        self.assertEqual(len(prompts), 2)
        # Check default prompts
        self.assertTrue(any(p.name == "help" for p in prompts))
        self.assertTrue(any(p.name == "assistant" for p in prompts))
        
        # Help prompt should have optional topic parameter
        help_prompt = next(p for p in prompts if p.name == "help")
        self.assertEqual(len(help_prompt.parameters), 1)
        self.assertEqual(help_prompt.parameters[0].name, "topic")
        self.assertFalse(help_prompt.parameters[0].required)
        
        # Assistant prompt should have required query parameter
        assistant_prompt = next(p for p in prompts if p.name == "assistant")
        self.assertEqual(len(assistant_prompt.parameters), 1)
        self.assertEqual(assistant_prompt.parameters[0].name, "query")
        self.assertTrue(assistant_prompt.parameters[0].required)


if __name__ == '__main__':
    unittest.main(verbosity=2)