#!/usr/bin/env python3
"""
Test suite for productivity-tracker MCP Server

Tests all tools, resources, and functionality to ensure the MCP works correctly.
Requirements: A comprehensive time tracking MCP that helps users log work sessions, categorize activities, generate reports, and analyze productivity patterns. It should track task duration, project categories, and provide insights like daily/weekly summaries.

Run with: python3 test.py
"""

import asyncio
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent.parent / "productivity-tracker"
sys.path.insert(0, str(project_dir))

# Import the MCP server after setting up the path
try:
    from server import mcp
except ImportError as e:
    print(f"❌ Failed to import MCP server: {e}")
    print(f"   Make sure server.py exists in {project_dir}")
    sys.exit(1)

# Test utilities
class MockContext:
    """Mock context for testing MCP tools"""
    def __init__(self):
        self.logs = []
        self.progress = []
    
    async def info(self, msg):
        self.logs.append(msg)
    
    async def report_progress(self, current, total, msg):
        self.progress.append((current, total, msg))
    
    async def read_resource(self, uri):
        return {"uri": uri, "content": "mock resource content"}


# Test functions
async def test_server_initialization():
    """Test that the MCP server can be initialized"""
    print("Testing server initialization...")
    try:
        assert mcp.name == "productivity-tracker"
        assert hasattr(mcp, 'run')
        print("  ✅ Server initialization test passed")
        return True
    except Exception as e:
        print(f"  ❌ Server initialization failed: {e}")
        return False


async def test_monitor_productivity():
    """Test monitor_productivity: Monitor operation for productivity.

Domain: productivity
Related operations: aggregating

TODO: Cla..."""
    print(f"\nTesting monitor_productivity...")
    
    # Get the tool from the MCP server
    try:
        tool = await mcp.get_tool("monitor_productivity")
        if not tool:
            print(f"  ❌ Tool monitor_productivity not found in MCP server")
            return False
        tool_func = tool.fn
    except Exception as e:
        print(f"  ❌ Could not access monitor_productivity: {e}")
        return False
    
    ctx = MockContext()
    passed = 0
    failed = 0
    
    # Test 1: Valid inputs
    try:
        result = await tool_func(
            ctx=ctx,
        target="test_value",
        interval=42,
        threshold="test_value"
        )
        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert any(key in result for key in ["success", "status", "data", "result"]), \
            "Result should contain success, status, data, or result key"
        print("  ✅ Valid input test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ Valid input test failed: {e}")
        failed += 1

    
    # Test 2: Missing required parameters
    try:
        # Call without required parameter: target
        result = await tool_func(ctx=ctx)
        print(f"  ❌ Should have failed with missing required parameter")
        failed += 1
    except TypeError as e:
        if "target" in str(e):
            print(f"  ✅ Missing parameter validation passed")
            passed += 1
        else:
            print(f"  ❌ Wrong error for missing parameter: {e}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Unexpected error for missing parameter: {e}")
        failed += 1

    
    # Test 3: Edge cases
    # TODO: Claude, add more specific edge case tests based on the requirements:
    # - Test with empty strings for string parameters
    # - Test with None for optional parameters  
    # - Test with boundary values for numeric parameters
    # - Test with special characters if applicable
    # - Test error conditions specific to this tool's purpose
    
    print(f"  📊 monitor_productivity tests: {passed} passed, {failed} failed")
    return failed == 0


async def test_analyze_data():
    """Test analyze_data: Process operation for data.

Domain: productivity
Related operations: aggregating

TODO: Claude, imp..."""
    print(f"\nTesting analyze_data...")
    
    # Get the tool from the MCP server
    try:
        tool = await mcp.get_tool("analyze_data")
        if not tool:
            print(f"  ❌ Tool analyze_data not found in MCP server")
            return False
        tool_func = tool.fn
    except Exception as e:
        print(f"  ❌ Could not access analyze_data: {e}")
        return False
    
    ctx = MockContext()
    passed = 0
    failed = 0
    
    # Test 1: Valid inputs
    try:
        result = await tool_func(
            ctx=ctx,
        input_data={"test": "data"},
        options="test_value"
        )
        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert any(key in result for key in ["success", "status", "data", "result"]), \
            "Result should contain success, status, data, or result key"
        print("  ✅ Valid input test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ Valid input test failed: {e}")
        failed += 1

    
    # Test 2: Missing required parameters
    try:
        # Call without required parameter: input_data
        result = await tool_func(ctx=ctx)
        print(f"  ❌ Should have failed with missing required parameter")
        failed += 1
    except TypeError as e:
        if "input_data" in str(e):
            print(f"  ✅ Missing parameter validation passed")
            passed += 1
        else:
            print(f"  ❌ Wrong error for missing parameter: {e}")
            failed += 1
    except Exception as e:
        print(f"  ❌ Unexpected error for missing parameter: {e}")
        failed += 1

    
    # Test 3: Edge cases
    # TODO: Claude, add more specific edge case tests based on the requirements:
    # - Test with empty strings for string parameters
    # - Test with None for optional parameters  
    # - Test with boundary values for numeric parameters
    # - Test with special characters if applicable
    # - Test error conditions specific to this tool's purpose
    
    print(f"  📊 analyze_data tests: {passed} passed, {failed} failed")
    return failed == 0


async def test_get_status():
    """Test get_status: Get status information for productivity

TODO: Claude, implement based on requirements..."""
    print(f"\nTesting get_status...")
    
    # Get the tool from the MCP server
    try:
        tool = await mcp.get_tool("get_status")
        if not tool:
            print(f"  ❌ Tool get_status not found in MCP server")
            return False
        tool_func = tool.fn
    except Exception as e:
        print(f"  ❌ Could not access get_status: {e}")
        return False
    
    ctx = MockContext()
    passed = 0
    failed = 0
    
    # Test 1: Valid inputs
    try:
        result = await tool_func(
            ctx=ctx,
        detailed=True
        )
        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert any(key in result for key in ["success", "status", "data", "result"]), \
            "Result should contain success, status, data, or result key"
        print("  ✅ Valid input test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ Valid input test failed: {e}")
        failed += 1

    
    # Test 3: Edge cases
    # TODO: Claude, add more specific edge case tests based on the requirements:
    # - Test with empty strings for string parameters
    # - Test with None for optional parameters  
    # - Test with boundary values for numeric parameters
    # - Test with special characters if applicable
    # - Test error conditions specific to this tool's purpose
    
    print(f"  📊 get_status tests: {passed} passed, {failed} failed")
    return failed == 0


async def test_resources():
    """Test that MCP resources are accessible"""
    print(f"\nTesting resources...")
    
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


async def test_prompts():
    """Test that MCP prompts are defined"""
    print(f"\nTesting prompts...")
    
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


async def run_all_tests():
    """Run all test cases"""
    print("=" * 50)
    print(f"🧪 Running MCP Server Tests for productivity-tracker")
    print("=" * 50)
    
    # List all tests to run
    tests = [
        ("Server Initialization", test_server_initialization),
        ("monitor_productivity", test_monitor_productivity),
        ("analyze_data", test_analyze_data),
        ("get_status", test_get_status),
        ("Resources", test_resources),
        ("Prompts", test_prompts),
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
            print(f"\n❌ {test_name} crashed: {e}")
            total_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Summary: {total_passed}/{len(tests)} passed")
    print("=" * 50)
    
    if total_failed > 0:
        print(f"\n⚠️  {total_failed} test(s) failed!")
        print("\nNext steps:")
        print("1. Check the error messages above")
        print("2. Fix the implementation in server.py")
        print("3. Run the tests again: python test.py")
        print("4. All tests must pass before the MCP is ready")
        return 1
    else:
        print("\n✅ All tests passed! The MCP server is ready to use.")
        print("\nYou can now:")
        print("1. Add it to Claude Desktop (see help.md)")
        print("2. Add more specific test cases based on your use case")
        print("3. Test with real data")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
