"""Integration tests for KEN-MCP generator"""

import unittest

from ken_mcp.core.analyzer import analyze_and_plan


class TestGeneratorIntegration(unittest.TestCase):
    """Test the main generator integration"""
    
    def test_analyze_requirements_basic_integration(self):
        """Test basic requirements analysis integration"""
        plan = analyze_and_plan("Create a simple calculator MCP")
        
        self.assertIsNotNone(plan)
        self.assertIn("calculator", plan.description.lower())
        self.assertGreater(len(plan.tools), 0)
    
    def test_analyze_requirements_with_resources(self):
        """Test requirements analysis with resources"""
        plan = analyze_and_plan("Create a calculator MCP", include_resources=True)
        
        self.assertIsNotNone(plan)
        self.assertGreater(len(plan.resources), 0)
    
    def test_analyze_requirements_without_prompts(self):
        """Test requirements analysis without prompts"""
        plan = analyze_and_plan("Create a calculator MCP", include_prompts=False)
        
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan.prompts), 0)


if __name__ == "__main__":
    unittest.main()