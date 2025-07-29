"""
Test generation for KEN-MCP
Handles generation of test.py with comprehensive test cases
"""

from pathlib import Path
from typing import List, Dict
import stat

from ken_mcp.core.models import GenerationPlan, ToolDefinition
from ken_mcp.templates.constants import TEST_FILE_HEADER, TEST_MOCK_CONTEXT
from ken_mcp.utils.text import escape_for_docstring


def generate_test_file(project_path: Path, plan: GenerationPlan, project_name: str) -> None:
    """Generate test.py with comprehensive test cases
    
    Args:
        project_path: Path to project directory
        plan: Generation plan with tools, resources, etc.
        project_name: Name of the project
    """
    test_content = generate_test_content(plan, project_name)
    test_file = project_path / "test.py"
    test_file.write_text(test_content)
    
    # Make executable
    test_file.chmod(test_file.stat().st_mode | stat.S_IEXEC)


def generate_test_content(plan: GenerationPlan, project_name: str) -> str:
    """Generate the complete test file content
    
    Args:
        plan: Generation plan
        project_name: Name of the project
        
    Returns:
        Complete test file content
    """
    # Build test file header
    content = TEST_FILE_HEADER.format(
        project_name=project_name,
        requirements=escape_for_docstring(plan.original_requirements)
    )
    
    # Add mock context
    content += "\n" + TEST_MOCK_CONTEXT + "\n"
    
    # Add server initialization test
    content += generate_initialization_test(project_name)
    
    # Add test for each tool
    for tool in plan.tools:
        content += generate_tool_test(tool)
    
    # Add resource tests if any
    if plan.resources:
        content += generate_resource_test()
    
    # Add prompt tests if any
    if plan.prompts:
        content += generate_prompt_test()
    
    # Add test runner
    content += generate_test_runner(plan, project_name)
    
    return content


def generate_initialization_test(project_name: str) -> str:
    """Generate server initialization test
    
    Args:
        project_name: Name of the project
        
    Returns:
        Test function code
    """
    return f'''
# Test functions
async def test_server_initialization():
    """Test that the MCP server can be initialized"""
    print("Testing server initialization...")
    try:
        assert mcp.name == "{project_name}"
        assert hasattr(mcp, 'run')
        print("  ✅ Server initialization test passed")
        return True
    except Exception as e:
        print(f"  ❌ Server initialization failed: {{e}}")
        return False
'''


def generate_tool_test(tool: ToolDefinition) -> str:
    """Generate test for a specific tool
    
    Args:
        tool: Tool definition
        
    Returns:
        Test function code
    """
    tool_name = tool.name
    tool_desc = escape_for_docstring(tool.description[:100])
    
    # Generate test parameters
    test_params = generate_test_parameters(tool.parameters)
    params_str = ",\n".join(f"        {k}={v}" for k, v in test_params.items())
    
    # Identify required parameters for missing param test
    required_params = [p for p in tool.parameters if p.required and p.name != "ctx"]
    
    test_code = f'''

async def test_{tool_name}():
    """Test {tool_name}: {tool_desc}..."""
    print(f"\\nTesting {tool_name}...")
    
    # Get the tool from the MCP server
    try:
        tool = await mcp.get_tool("{tool_name}")
        if not tool:
            print(f"  ❌ Tool {tool_name} not found in MCP server")
            return False
        tool_func = tool.fn
    except Exception as e:
        print(f"  ❌ Could not access {tool_name}: {{e}}")
        return False
    
    ctx = MockContext()
    passed = 0
    failed = 0
    
    # Test 1: Valid inputs
    try:
        result = await tool_func(
            ctx=ctx,
{params_str}
        )
        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert any(key in result for key in ["success", "status", "data", "result"]), \\
            "Result should contain success, status, data, or result key"
        print("  ✅ Valid input test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ Valid input test failed: {{e}}")
        failed += 1
'''
    
    # Add missing parameter test if there are required params
    if required_params:
        first_required = required_params[0].name
        test_code += f'''
    
    # Test 2: Missing required parameters
    try:
        # Call without required parameter: {first_required}
        result = await tool_func(ctx=ctx)
        print(f"  ❌ Should have failed with missing required parameter")
        failed += 1
    except TypeError as e:
        if "{first_required}" in str(e):
            print(f"  ✅ Missing parameter validation passed")
            passed += 1
        else:
            print(f"  ❌ Wrong error for missing parameter: {{e}}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Unexpected error for missing parameter: {{e}}")
        failed += 1
'''
    
    # Add edge case reminder
    test_code += f'''
    
    # Test 3: Edge cases
    # TODO: Claude, add more specific edge case tests based on the requirements:
    # - Test with empty strings for string parameters
    # - Test with None for optional parameters  
    # - Test with boundary values for numeric parameters
    # - Test with special characters if applicable
    # - Test error conditions specific to this tool's purpose
    
    print(f"  📊 {tool_name} tests: {{passed}} passed, {{failed}} failed")
    return failed == 0
'''
    
    return test_code


def generate_test_parameters(parameters: List) -> Dict[str, str]:
    """Generate test values for parameters
    
    Args:
        parameters: List of parameter definitions
        
    Returns:
        Dictionary of parameter names to test values
    """
    test_params = {}
    
    for param in parameters:
        if param.name == "ctx":
            continue
            
        test_value = generate_test_value(param.name, param.type, param.description)
        test_params[param.name] = test_value
    
    return test_params


def generate_test_value(param_name: str, param_type: str, param_desc: str = "") -> str:
    """Generate appropriate test value based on parameter
    
    Args:
        param_name: Parameter name
        param_type: Parameter type
        param_desc: Parameter description
        
    Returns:
        Test value as string
    """
    param_lower = param_name.lower()
    type_lower = param_type.lower()
    
    # Name-based heuristics
    if "file" in param_lower or "path" in param_lower:
        return '"/tmp/test_file.txt"'
    elif "url" in param_lower or "endpoint" in param_lower:
        return '"https://example.com/api"'
    elif "email" in param_lower:
        return '"test@example.com"'
    elif "name" in param_lower:
        return '"Test Name"'
    elif "id" in param_lower:
        return '"test_id_123"'
    elif "key" in param_lower:
        return '"test_key_abc"'
    elif "token" in param_lower:
        return '"test_token_xyz"'
    
    # Type-based defaults
    if "str" in type_lower:
        return '"test_value"'
    elif "int" in type_lower:
        return "42"
    elif "float" in type_lower:
        return "3.14"
    elif "bool" in type_lower:
        return "True"
    elif "list" in type_lower:
        return '["item1", "item2"]'
    elif "dict" in type_lower:
        return '{"key": "value"}'
    elif "any" in type_lower:
        return '{"test": "data"}'
    else:
        return '"test_input"'


def generate_resource_test() -> str:
    """Generate test for resources
    
    Returns:
        Resource test code
    """
    return '''

async def test_resources():
    """Test that MCP resources are accessible"""
    print(f"\\nTesting resources...")
    
    try:
        # Get available resources
        resources = await mcp.get_resources()
        assert len(resources) > 0, "No resources defined"
        print(f"  ✅ Found {len(resources)} resources")
        
        # Test each resource
        for uri, resource in resources.items():
            print(f"  Testing resource: {uri}")
            try:
                result = await resource.fn()
                print(f"    ✅ Resource {uri} returned data")
            except Exception as e:
                print(f"    ❌ Resource {uri} failed: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Resource test failed: {e}")
        return False
'''


def generate_prompt_test() -> str:
    """Generate test for prompts
    
    Returns:
        Prompt test code
    """
    return '''

async def test_prompts():
    """Test that MCP prompts are defined"""
    print(f"\\nTesting prompts...")
    
    try:
        # Get available prompts
        prompts = await mcp.get_prompts()
        assert len(prompts) > 0, "No prompts defined"
        print(f"  ✅ Found {len(prompts)} prompts")
        
        # Test each prompt
        for name, prompt in prompts.items():
            print(f"  Testing prompt: {name}")
            try:
                # Prompts typically return strings, not async
                result = prompt.fn()
                print(f"    ✅ Prompt {name} returned template")
            except Exception as e:
                print(f"    ❌ Prompt {name} failed: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Prompt test failed: {e}")
        return False
'''


def generate_test_runner(plan: GenerationPlan, project_name: str) -> str:
    """Generate the main test runner
    
    Args:
        plan: Generation plan
        project_name: Project name
        
    Returns:
        Test runner code
    """
    # Build test list
    tests = [
        '        ("Server Initialization", test_server_initialization),'
    ]
    
    for tool in plan.tools:
        tests.append(f'        ("{tool.name}", test_{tool.name}),')
    
    if plan.resources:
        tests.append('        ("Resources", test_resources),')
    
    if plan.prompts:
        tests.append('        ("Prompts", test_prompts),')
    
    tests_str = "\n".join(tests)
    
    return f'''

async def run_all_tests():
    """Run all test cases"""
    print("=" * 50)
    print(f"🧪 Running MCP Server Tests for {project_name}")
    print("=" * 50)
    
    # List all tests to run
    tests = [
{tests_str}
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                total_passed += 1
            else:
                total_failed += 1
        except Exception as e:
            print(f"\\n❌ {{test_name}} crashed: {{e}}")
            total_failed += 1
    
    # Summary
    print("\\n" + "=" * 50)
    print(f"📊 Test Summary: {{total_passed}}/{{len(tests)}} passed")
    print("=" * 50)
    
    if total_failed > 0:
        print(f"\\n⚠️  {{total_failed}} test(s) failed!")
        print("\\nNext steps:")
        print("1. Check the error messages above")
        print("2. Fix the implementation in server.py")
        print("3. Run the tests again: python test.py")
        print("4. All tests must pass before the MCP is ready")
        return 1
    else:
        print("\\n✅ All tests passed! The MCP server is ready to use.")
        print("\\nYou can now:")
        print("1. Add it to Claude Desktop (see help.md)")
        print("2. Add more specific test cases based on your use case")
        print("3. Test with real data")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
'''


def generate_test_file_to_scripts(
    scripts_path: Path, 
    project_path: Path, 
    plan: GenerationPlan, 
    project_name: str
) -> None:
    """Generate test.py in scripts directory with correct import paths
    
    Args:
        scripts_path: Path to scripts directory
        project_path: Path to MCP project directory
        plan: Generation plan with tools, resources, etc.
        project_name: Name of the project
    """
    test_content = generate_test_content_for_scripts(plan, project_name, project_path.name)
    test_file = scripts_path / "test.py"
    test_file.write_text(test_content)
    
    # Make executable
    test_file.chmod(test_file.stat().st_mode | stat.S_IEXEC)


def generate_test_content_for_scripts(plan: GenerationPlan, project_name: str, project_dir_name: str) -> str:
    """Generate test file content for scripts directory with correct imports
    
    Args:
        plan: Generation plan
        project_name: Name of the project
        project_dir_name: Name of the project directory
        
    Returns:
        Complete test file content with updated import paths
    """
    # Build test file header with updated import path
    content = f'''#!/usr/bin/env python3
"""
Test suite for {project_name} MCP Server

Tests all tools, resources, and functionality to ensure the MCP works correctly.
Requirements: {escape_for_docstring(plan.original_requirements)}

Run with: python3 test.py
"""

import asyncio
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent.parent / "{project_dir_name}"
sys.path.insert(0, str(project_dir))

# Import the MCP server after setting up the path
try:
    from server import mcp
except ImportError as e:
    print(f"❌ Failed to import MCP server: {{e}}")
    print(f"   Make sure server.py exists in {{project_dir}}")
    sys.exit(1)
'''
    
    # Add mock context
    content += "\n" + TEST_MOCK_CONTEXT + "\n"
    
    # Add server initialization test
    content += generate_initialization_test(project_name)
    
    # Add test for each tool
    for tool in plan.tools:
        content += generate_tool_test(tool)
    
    # Add resource tests if any
    if plan.resources:
        content += generate_resource_test()
    
    # Add prompt tests if any
    if plan.prompts:
        content += generate_prompt_test()
    
    # Add test runner
    content += generate_test_runner(plan, project_name)
    
    return content