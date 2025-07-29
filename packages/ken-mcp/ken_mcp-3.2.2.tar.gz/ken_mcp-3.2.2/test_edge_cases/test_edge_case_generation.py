#!/usr/bin/env python3
"""
Test script for edge case MCP generation
Directly tests the refactored KEN-MCP modules
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import refactored modules directly
from ken_mcp.core.models import ProjectConfig
from ken_mcp.core.orchestrator import generate_mcp_server
from ken_mcp.utils.validation import validate_project

# Mock Context for testing
class MockContext:
    async def info(self, msg):
        print(f"[INFO] {msg}")
    
    async def report_progress(self, current, total, msg):
        print(f"[PROGRESS {current}/{total}] {msg}")


async def test_edge_case_1():
    """Test Edge Case 1: Multi-Modal System Monitor"""
    print("\n" + "="*60)
    print("EDGE CASE 1: Multi-Modal System Monitor")
    print("="*60)
    
    requirements = """Create an MCP that monitors system resources (CPU, memory, disk), 
    scrapes web APIs for cryptocurrency prices, stores historical data in a SQLite database, 
    generates real-time alerts via webhooks, and provides both REST API endpoints and 
    WebSocket streaming. Include authentication, rate limiting, and data visualization capabilities."""
    
    config = ProjectConfig(
        requirements=requirements,
        project_name="system-monitor-mcp",
        output_dir="test_edge_cases",
        include_resources=True,
        include_prompts=True,
        python_version="3.10",
        additional_dependencies=["psutil", "aiohttp", "websockets", "plotly"]
    )
    
    # Validate config
    errors = config.validate()
    if errors:
        print(f"Config validation errors: {errors}")
        return False
    
    # Generate the MCP
    ctx = MockContext()
    result = await generate_mcp_server(ctx, config)
    
    print(f"\nGeneration result:")
    print(f"- Success: {result.success}")
    print(f"- Project path: {result.project_path}")
    print(f"- Tools generated: {result.tools_generated}")
    print(f"- Resources generated: {result.resources_generated}")
    print(f"- Prompts generated: {result.prompts_generated}")
    
    if result.error:
        print(f"- Error: {result.error}")
    
    return result.success


async def test_edge_case_2():
    """Test Edge Case 2: AI-Powered Document Processor"""
    print("\n" + "="*60)
    print("EDGE CASE 2: AI-Powered Document Processor")
    print("="*60)
    
    requirements = """Build an MCP that processes multiple document formats (PDF, Word, Excel, 
    images with OCR), extracts structured data using NLP, categorizes content using machine 
    learning, manages document workflows with approval chains, integrates with cloud storage 
    (S3, Google Drive), sends email notifications, and provides a GraphQL API with subscription 
    support for real-time updates."""
    
    config = ProjectConfig(
        requirements=requirements,
        project_name="document-processor-mcp",
        output_dir="test_edge_cases",
        include_resources=True,
        include_prompts=True,
        python_version="3.10",
        additional_dependencies=["pypdf2", "python-docx", "openpyxl", "pytesseract", "boto3"]
    )
    
    # Validate config
    errors = config.validate()
    if errors:
        print(f"Config validation errors: {errors}")
        return False
    
    # Generate the MCP
    ctx = MockContext()
    result = await generate_mcp_server(ctx, config)
    
    print(f"\nGeneration result:")
    print(f"- Success: {result.success}")
    print(f"- Project path: {result.project_path}")
    print(f"- Tools generated: {result.tools_generated}")
    print(f"- Resources generated: {result.resources_generated}")
    print(f"- Prompts generated: {result.prompts_generated}")
    
    if result.error:
        print(f"- Error: {result.error}")
    
    return result.success


def validate_generated_mcp(project_name):
    """Validate the generated MCP structure and syntax"""
    print(f"\n[VALIDATING] {project_name}")
    
    project_path = Path("test_edge_cases") / project_name
    
    # Check if project exists
    if not project_path.exists():
        print(f"❌ Project directory not found: {project_path}")
        return False
    
    # Validate project structure
    validation_result = validate_project(project_path)
    
    print(f"- Valid: {validation_result['valid']}")
    print(f"- Files checked: {validation_result['files_checked']}")
    
    if validation_result['issues']:
        print("- Issues:")
        for issue in validation_result['issues']:
            print(f"  • {issue}")
    
    if validation_result['warnings']:
        print("- Warnings:")
        for warning in validation_result['warnings']:
            print(f"  • {warning}")
    
    # Check Python syntax
    if (project_path / "server.py").exists():
        import py_compile
        try:
            py_compile.compile(str(project_path / "server.py"), doraise=True)
            print("✅ server.py syntax is valid")
        except py_compile.PyCompileError as e:
            print(f"❌ server.py syntax error: {e}")
            return False
    
    # Check if test.py is valid
    if (project_path / "test.py").exists():
        try:
            py_compile.compile(str(project_path / "test.py"), doraise=True)
            print("✅ test.py syntax is valid")
        except py_compile.PyCompileError as e:
            print(f"❌ test.py syntax error: {e}")
            return False
    
    return validation_result['valid']


async def main():
    """Run all edge case tests"""
    print("Testing Refactored KEN-MCP with Edge Cases")
    print("==========================================")
    
    # Test Edge Case 1
    success1 = await test_edge_case_1()
    if success1:
        valid1 = validate_generated_mcp("system-monitor-mcp")
    else:
        valid1 = False
    
    # Test Edge Case 2
    success2 = await test_edge_case_2()
    if success2:
        valid2 = validate_generated_mcp("document-processor-mcp")
    else:
        valid2 = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Edge Case 1 (System Monitor):")
    print(f"  - Generation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"  - Validation: {'✅ PASS' if valid1 else '❌ FAIL'}")
    print(f"\nEdge Case 2 (Document Processor):")
    print(f"  - Generation: {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"  - Validation: {'✅ PASS' if valid2 else '❌ FAIL'}")
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all([success1, valid1, success2, valid2]) else '❌ SOME TESTS FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())