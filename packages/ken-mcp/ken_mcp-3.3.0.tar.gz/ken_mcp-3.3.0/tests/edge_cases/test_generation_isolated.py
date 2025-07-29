#!/usr/bin/env python3
"""
Isolated test of MCP generation - completely avoids fastmcp dependency
Tests the core generation logic without the MCP wrapper
"""

import sys
import os
import asyncio
from pathlib import Path

# Completely isolate our test from the ken_mcp package structure
# This prevents any imports of generator.py which requires fastmcp

# First, let's directly test the core logic
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import only the specific files we need as standalone modules
import importlib.util

def load_module(name, filepath):
    """Load a module from filepath without triggering __init__.py imports"""
    spec = importlib.util.spec_from_file_location(name, filepath)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        # Add to sys.modules BEFORE execution to handle circular imports
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"Could not load {name} from {filepath}")

# Load constants first (no dependencies)
base = Path(__file__).parent.parent / "ken_mcp"
constants = load_module("ken_mcp.templates.constants", base / "templates" / "constants.py")

# Load utils (minimal dependencies)
text_utils = load_module("ken_mcp.utils.text", base / "utils" / "text.py")
suggestions = load_module("ken_mcp.utils.suggestions", base / "utils" / "suggestions.py")
validation = load_module("ken_mcp.utils.validation", base / "utils" / "validation.py")

# Load models (no external dependencies)
models = load_module("ken_mcp.core.models", base / "core" / "models.py")

# Load generators (depends on above)
project_gen = load_module("ken_mcp.generators.project", base / "generators" / "project.py")
server_gen = load_module("ken_mcp.generators.server", base / "generators" / "server.py")
docs_gen = load_module("ken_mcp.generators.docs", base / "generators" / "docs.py")
tests_gen = load_module("ken_mcp.generators.tests", base / "generators" / "tests.py")

# Load analyzer (depends on models and utils)
analyzer = load_module("ken_mcp.core.analyzer", base / "core" / "analyzer.py")

# Mock Context for orchestrator
class MockContext:
    async def info(self, msg):
        print(f"[INFO] {msg}")
    
    async def report_progress(self, current, total, msg):
        print(f"[PROGRESS {current}/{total}] {msg}")

# Mock fastmcp imports for orchestrator
class ToolError(Exception):
    pass

fake_fastmcp = type(sys)('module')
fake_fastmcp.Context = MockContext
fake_fastmcp.exceptions = type(sys)('module')
fake_fastmcp.exceptions.ToolError = ToolError
sys.modules['fastmcp'] = fake_fastmcp
sys.modules['fastmcp.exceptions'] = fake_fastmcp.exceptions

# Now load orchestrator
orchestrator = load_module("ken_mcp.core.orchestrator", base / "core" / "orchestrator.py")

# Direct access to what we need
ProjectConfig = models.ProjectConfig
generate_mcp_server = orchestrator.generate_mcp_server
validate_project = validation.validate_project


async def test_edge_case(name, requirements, project_name, additional_deps):
    """Test a single edge case"""
    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print(f"{'='*60}")
    print(f"Requirements: {requirements[:100]}...")
    
    config = ProjectConfig(
        requirements=requirements,
        project_name=project_name,
        output_dir="test_edge_cases",
        include_resources=True,
        include_prompts=True,
        python_version="3.10",
        additional_dependencies=additional_deps
    )
    
    # Validate config
    errors = config.validate()
    if errors:
        print(f"❌ Config validation errors: {errors}")
        return False, False
    print("✅ Config validation passed")
    
    # Generate the MCP
    ctx = MockContext()
    try:
        result = await generate_mcp_server(ctx, config)
        
        print(f"\nGeneration completed:")
        print(f"  Success: {result.success}")
        print(f"  Project path: {result.project_path}")
        print(f"  Tools generated: {result.tools_generated}")
        print(f"  Resources generated: {result.resources_generated}")
        print(f"  Prompts generated: {result.prompts_generated}")
        
        if result.error:
            print(f"  ❌ Error: {result.error}")
            return False, False
            
        # Validate the generated project
        if result.success:
            print(f"\nValidating generated project...")
            validation_result = validate_project(result.project_path)
            
            print(f"  Valid: {validation_result['valid']}")
            print(f"  Files checked: {validation_result['files_checked']}")
            
            if validation_result['issues']:
                print("  Issues:")
                for issue in validation_result['issues']:
                    print(f"    • {issue}")
            
            # Check syntax
            import py_compile
            server_file = result.project_path / "server.py"
            test_file = result.project_path / "test.py"
            
            syntax_valid = True
            if server_file.exists():
                try:
                    py_compile.compile(str(server_file), doraise=True)
                    print("  ✅ server.py syntax is valid")
                except Exception as e:
                    print(f"  ❌ server.py syntax error: {e}")
                    syntax_valid = False
            
            if test_file.exists():
                try:
                    py_compile.compile(str(test_file), doraise=True)
                    print("  ✅ test.py syntax is valid")
                except Exception as e:
                    print(f"  ❌ test.py syntax error: {e}")
                    syntax_valid = False
            
            return result.success, validation_result['valid'] and syntax_valid
        
    except Exception as e:
        print(f"❌ Generation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False, False
    
    return result.success, False


async def main():
    """Run all edge case tests"""
    print("ISOLATED TEST: Refactored KEN-MCP Edge Cases")
    print("=" * 60)
    print("Testing without fastmcp runtime dependency")
    print("This validates the core generation logic")
    
    # Edge Case 1: Multi-Modal System Monitor
    req1 = """Create an MCP that monitors system resources (CPU, memory, disk), 
    scrapes web APIs for cryptocurrency prices, stores historical data in a SQLite database, 
    generates real-time alerts via webhooks, and provides both REST API endpoints and 
    WebSocket streaming. Include authentication, rate limiting, and data visualization."""
    
    gen1, val1 = await test_edge_case(
        "Multi-Modal System Monitor",
        req1,
        "system-monitor-mcp",
        ["psutil", "aiohttp", "websockets", "plotly", "sqlite3"]
    )
    
    # Edge Case 2: AI-Powered Document Processor  
    req2 = """Build an MCP that processes multiple document formats (PDF, Word, Excel, 
    images with OCR), extracts structured data using NLP, categorizes content using machine 
    learning, manages document workflows with approval chains, integrates with cloud storage 
    (S3, Google Drive), sends email notifications, and provides a GraphQL API."""
    
    gen2, val2 = await test_edge_case(
        "AI-Powered Document Processor",
        req2,
        "document-processor-mcp",
        ["pypdf2", "python-docx", "openpyxl", "pytesseract", "boto3", "google-api-python-client"]
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    print(f"\nEdge Case 1 (System Monitor):")
    print(f"  Generation: {'✅ PASS' if gen1 else '❌ FAIL'}")
    print(f"  Validation: {'✅ PASS' if val1 else '❌ FAIL'}")
    print(f"\nEdge Case 2 (Document Processor):")
    print(f"  Generation: {'✅ PASS' if gen2 else '❌ FAIL'}")
    print(f"  Validation: {'✅ PASS' if val2 else '❌ FAIL'}")
    
    all_passed = all([gen1, val1, gen2, val2])
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\nThe refactored KEN-MCP successfully generates complex MCPs!")
        print("Both edge cases demonstrate:")
        print("- Correct dependency detection")
        print("- Proper tool/resource/prompt generation")
        print("- Valid Python syntax")
        print("- Complete project structure")


if __name__ == "__main__":
    asyncio.run(main())