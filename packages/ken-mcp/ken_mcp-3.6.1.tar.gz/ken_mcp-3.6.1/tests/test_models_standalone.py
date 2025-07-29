#!/usr/bin/env python3
"""
Tests for core data models
Following CLAUDE.md: test_functionName_condition_expectedResult
"""

import sys
import unittest
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import module directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "models", 
    Path(__file__).parent.parent / "ken_mcp" / "core" / "models.py"
)
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

# Import classes
ParameterDefinition = models.ParameterDefinition
ToolDefinition = models.ToolDefinition
ResourceDefinition = models.ResourceDefinition
PromptDefinition = models.PromptDefinition
GenerationPlan = models.GenerationPlan
ProjectConfig = models.ProjectConfig
GenerationResult = models.GenerationResult
ValidationResult = models.ValidationResult
TestCase = models.TestCase


class TestModels(unittest.TestCase):
    """Test data models - 100% coverage for business logic"""
    
    # ParameterDefinition tests
    def test_ParameterDefinition_withDefaults_createsCorrectly(self):
        """Test parameter with defaults creates correctly"""
        param = ParameterDefinition(
            name="test_param",
            type="str",
            description="A test parameter"
        )
        self.assertEqual(param.name, "test_param")
        self.assertEqual(param.type, "str")
        self.assertEqual(param.description, "A test parameter")
        self.assertIsNone(param.default)
        self.assertTrue(param.required)
    
    def test_ParameterDefinition_optional_setsRequiredFalse(self):
        """Test optional parameter sets required to False"""
        param = ParameterDefinition(
            name="opt_param",
            type="Optional[str]",
            description="Optional parameter",
            default=None,
            required=False
        )
        self.assertFalse(param.required)
        self.assertIsNone(param.default)
    
    # ToolDefinition tests
    def test_ToolDefinition_toDict_returnsCorrectStructure(self):
        """Test to_dict returns correct structure"""
        tool = ToolDefinition(
            name="test_tool",
            description="Test tool description",
            parameters=[
                ParameterDefinition("param1", "str", "First param"),
                ParameterDefinition("param2", "int", "Second param", default=42)
            ]
        )
        
        result = tool.to_dict()
        self.assertEqual(result["name"], "test_tool")
        self.assertEqual(result["description"], "Test tool description")
        self.assertEqual(len(result["parameters"]), 2)
        self.assertEqual(result["parameters"][0]["name"], "param1")
        self.assertEqual(result["parameters"][1]["default"], 42)
        self.assertEqual(result["implementation"], "boilerplate")
    
    def test_ToolDefinition_emptyParameters_worksCorrectly(self):
        """Test tool with no parameters works"""
        tool = ToolDefinition(
            name="simple_tool",
            description="No parameters"
        )
        result = tool.to_dict()
        self.assertEqual(len(result["parameters"]), 0)
    
    # ResourceDefinition tests
    def test_ResourceDefinition_toDict_returnsCorrectStructure(self):
        """Test resource to_dict returns correct structure"""
        resource = ResourceDefinition(
            uri_pattern="data://items",
            description="List of items"
        )
        
        result = resource.to_dict()
        self.assertEqual(result["uri_pattern"], "data://items")
        self.assertEqual(result["description"], "List of items")
        self.assertEqual(result["implementation"], "boilerplate")
    
    # PromptDefinition tests
    def test_PromptDefinition_toDict_includesParameters(self):
        """Test prompt to_dict includes parameters"""
        prompt = PromptDefinition(
            name="help",
            description="Get help",
            parameters=[
                ParameterDefinition("topic", "Optional[str]", "Help topic", default=None)
            ]
        )
        
        result = prompt.to_dict()
        self.assertEqual(result["name"], "help")
        self.assertEqual(result["description"], "Get help")
        self.assertEqual(len(result["parameters"]), 1)
        self.assertIsNone(result["parameters"][0]["default"])
    
    # GenerationPlan tests
    def test_GenerationPlan_toDict_includesAllFields(self):
        """Test plan to_dict includes all fields"""
        plan = GenerationPlan(
            description="Test MCP server",
            tools=[ToolDefinition("tool1", "Tool 1")],
            resources=[ResourceDefinition("res://test", "Test resource")],
            prompts=[PromptDefinition("prompt1", "Test prompt")],
            dependencies=["fastmcp", "requests"],
            original_requirements="Build a test server"
        )
        
        result = plan.to_dict()
        self.assertEqual(result["description"], "Test MCP server")
        self.assertEqual(len(result["tools"]), 1)
        self.assertEqual(len(result["resources"]), 1)
        self.assertEqual(len(result["prompts"]), 1)
        self.assertEqual(len(result["dependencies"]), 2)
        self.assertEqual(result["original_requirements"], "Build a test server")
    
    def test_GenerationPlan_emptyCollections_defaultsToEmpty(self):
        """Test plan with no items defaults to empty lists"""
        plan = GenerationPlan(description="Empty plan")
        
        result = plan.to_dict()
        self.assertEqual(len(result["tools"]), 0)
        self.assertEqual(len(result["resources"]), 0)
        self.assertEqual(len(result["prompts"]), 0)
        self.assertEqual(len(result["dependencies"]), 0)
    
    # ProjectConfig tests - Happy path
    def test_ProjectConfig_validate_validConfig_returnsEmpty(self):
        """Test valid config returns no errors"""
        config = ProjectConfig(
            requirements="Build a todo app",
            project_name="todo-app",
            python_version="3.10"
        )
        
        errors = config.validate()
        self.assertEqual(len(errors), 0)
    
    # ProjectConfig tests - Error cases
    def test_ProjectConfig_validate_emptyRequirements_returnsError(self):
        """Test empty requirements returns error"""
        config = ProjectConfig(
            requirements="",
            project_name="test-app"
        )
        
        errors = config.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Requirements cannot be empty" in e for e in errors))
    
    def test_ProjectConfig_validate_emptyProjectName_returnsError(self):
        """Test empty project name returns error"""
        config = ProjectConfig(
            requirements="Build something",
            project_name=""
        )
        
        errors = config.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("Project name cannot be empty" in e for e in errors))
    
    def test_ProjectConfig_validate_longProjectName_returnsError(self):
        """Test project name over 50 chars returns error"""
        config = ProjectConfig(
            requirements="Build app",
            project_name="a" * 51
        )
        
        errors = config.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("too long" in e for e in errors))
    
    def test_ProjectConfig_validate_invalidPythonVersion_returnsError(self):
        """Test invalid Python version format returns error"""
        config = ProjectConfig(
            requirements="Build app",
            project_name="test-app",
            python_version="3.10.1"  # Should be X.Y format
        )
        
        errors = config.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("format X.Y" in e for e in errors))
    
    # GenerationResult tests
    def test_GenerationResult_toDict_successCase_includesAllFields(self):
        """Test successful result includes all fields"""
        result = GenerationResult(
            success=True,
            project_path=Path("/tmp/test-project"),
            project_name="test-project",
            tools_generated=3,
            resources_generated=2,
            prompts_generated=1,
            validation={"valid": True, "issues": []},
            next_steps=["Step 1", "Step 2"]
        )
        
        dict_result = result.to_dict()
        self.assertTrue(dict_result["success"])
        self.assertEqual(dict_result["project_path"], "/tmp/test-project")
        self.assertEqual(dict_result["project_name"], "test-project")
        self.assertEqual(dict_result["tools_generated"], 3)
        self.assertIsNone(dict_result["error"])
    
    def test_GenerationResult_toDict_failureCase_includesError(self):
        """Test failure result includes error"""
        result = GenerationResult(
            success=False,
            project_path=Path("."),
            project_name="failed-project",
            error="Something went wrong"
        )
        
        dict_result = result.to_dict()
        self.assertFalse(dict_result["success"])
        self.assertEqual(dict_result["error"], "Something went wrong")
    
    # ValidationResult tests
    def test_ValidationResult_toDict_includesAllFields(self):
        """Test validation result includes all fields"""
        result = ValidationResult(
            valid=False,
            issues=["Missing file", "Syntax error"],
            warnings=["File not executable"],
            files_checked=5
        )
        
        dict_result = result.to_dict()
        self.assertFalse(dict_result["valid"])
        self.assertEqual(len(dict_result["issues"]), 2)
        self.assertEqual(len(dict_result["warnings"]), 1)
        self.assertEqual(dict_result["files_checked"], 5)
    
    # TestCase tests
    def test_TestCase_allFields_setCorrectly(self):
        """Test TestCase dataclass stores all fields"""
        test = TestCase(
            name="test_example",
            description="Example test",
            test_type="valid",
            parameters={"input": "test"},
            expected_behavior="Should return success"
        )
        
        self.assertEqual(test.name, "test_example")
        self.assertEqual(test.description, "Example test")
        self.assertEqual(test.test_type, "valid")
        self.assertEqual(test.parameters["input"], "test")
        self.assertEqual(test.expected_behavior, "Should return success")


if __name__ == '__main__':
    unittest.main(verbosity=2)