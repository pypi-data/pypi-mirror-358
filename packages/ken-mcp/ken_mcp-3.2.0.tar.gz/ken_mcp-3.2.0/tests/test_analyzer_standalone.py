#!/usr/bin/env python3
"""
Tests for requirements analyzer
Following CLAUDE.md: test_functionName_condition_expectedResult
"""

import unittest

# Standard imports
from ken_mcp.core.analyzer import analyze_and_plan


class TestAnalyzer(unittest.TestCase):
    """Test requirements analyzer - 100% coverage for business logic"""
    
    # analyze_and_plan tests - Happy path
    def test_analyze_and_plan_basicRequirements_returnsValidPlan(self):
        """Test basic requirements return valid plan"""
        plan = analyze_and_plan("Build a todo app")
        
        self.assertIn("todo app", plan.description)
        self.assertEqual(plan.original_requirements, "Build a todo app")
        self.assertEqual(len(plan.tools), 3)  # Default 3 tools
        self.assertIsInstance(plan.dependencies, list)  # Dependencies should be a list
    
    def test_analyze_and_plan_withResources_includesResources(self):
        """Test plan includes resources when requested"""
        plan = analyze_and_plan("Build a list manager", include_resources=True)
        
        self.assertGreater(len(plan.resources), 0)
    
    def test_analyze_and_plan_withPrompts_includesPrompts(self):
        """Test plan includes prompts when requested"""
        plan = analyze_and_plan("Build app with help", include_prompts=True)
        
        self.assertGreater(len(plan.prompts), 0)
    
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
        """Test long requirements are handled properly"""
        long_req = "Build a comprehensive application that does many things and has lots of features " * 10
        plan = analyze_and_plan(long_req)
        
        # Description should be reasonable length
        self.assertLess(len(plan.description), 500)
        # But original requirements preserved
        self.assertEqual(plan.original_requirements, long_req)
    
    def test_analyze_and_plan_emptyRequirements_handlesGracefully(self):
        """Test empty requirements are handled"""
        plan = analyze_and_plan("")
        
        self.assertIsNotNone(plan.description)
        self.assertEqual(plan.original_requirements, "")
        self.assertEqual(len(plan.tools), 3)  # Default tools
    
    def test_analyze_and_plan_specialChars_handlesGracefully(self):
        """Test special characters in requirements"""
        plan = analyze_and_plan("Build app with \"quotes\" and \\backslashes")
        
        self.assertIsNotNone(plan.description)
        self.assertEqual(len(plan.tools), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)