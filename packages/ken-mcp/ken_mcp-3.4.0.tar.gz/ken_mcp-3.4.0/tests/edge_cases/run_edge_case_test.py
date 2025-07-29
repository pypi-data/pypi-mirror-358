#!/usr/bin/env python3
"""
Direct test of KEN-MCP edge cases using the refactored modules
This script will generate 2 complex MCPs and validate them completely
"""

import sys
import os
import subprocess
from pathlib import Path
import shutil

# Add the MCP directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our modules directly
from ken_mcp.core.models import ProjectConfig
from ken_mcp.core.orchestrator import generate_mcp_server
from ken_mcp.core.analyzer import analyze_and_plan
from ken_mcp.utils.validation import validate_project, check_python_syntax

# Mock Context since we're not running under fastmcp
class MockContext:
    async def info(self, msg):
        print(f"[INFO] {msg}")
    
    async def report_progress(self, current, total, msg):
        print(f"[{current}/{total}] {msg}")


def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


async def generate_edge_case_mcp(name, requirements, project_name, dependencies):
    """Generate and validate a single edge case MCP"""
    print_section(f"Generating Edge Case: {name}")
    
    # Create configuration
    config = ProjectConfig(
        requirements=requirements,
        project_name=project_name,
        output_dir="test_edge_cases",
        include_resources=True,
        include_prompts=True,
        python_version="3.10",
        additional_dependencies=dependencies
    )
    
    # Validate configuration
    config_errors = config.validate()
    if config_errors:
        print(f"❌ Configuration errors: {config_errors}")
        return False
    
    print("✅ Configuration valid")
    
    # Generate the MCP
    ctx = MockContext()
    try:
        result = await generate_mcp_server(ctx, config)
        
        if not result.success:
            print(f"❌ Generation failed: {result.error}")
            return False
            
        print(f"\n✅ MCP Generated Successfully!")
        print(f"   Project path: {result.project_path}")
        print(f"   Tools generated: {result.tools_generated}")
        print(f"   Resources generated: {result.resources_generated}")
        print(f"   Prompts generated: {result.prompts_generated}")
        
        # Detailed validation
        return validate_generated_project(result.project_path, project_name)
        
    except Exception as e:
        print(f"❌ Exception during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_generated_project(project_path, project_name):
    """Thoroughly validate the generated project"""
    print(f"\n📋 Validating {project_name}...")
    
    all_valid = True
    
    # 1. Check project structure
    print("\n1️⃣ Checking file structure:")
    required_files = {
        "server.py": "Server implementation",
        "test.py": "Test suite",
        "README.md": "Project documentation",
        "help.md": "Setup and troubleshooting guide",
        "pyproject.toml": "Python project configuration",
        ".gitignore": "Git ignore file",
        ".env.example": "Environment variables template",
        "__init__.py": "Python package marker"
    }
    
    for filename, description in required_files.items():
        file_path = project_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {filename:<20} ({size:>6} bytes) - {description}")
        else:
            print(f"   ❌ {filename:<20} MISSING - {description}")
            all_valid = False
    
    # 2. Validate Python syntax
    print("\n2️⃣ Checking Python syntax:")
    for py_file in ["server.py", "test.py"]:
        file_path = project_path / py_file
        if file_path.exists():
            error = check_python_syntax(file_path)
            if error:
                print(f"   ❌ {py_file}: {error}")
                all_valid = False
            else:
                print(f"   ✅ {py_file}: Valid Python syntax")
    
    # 3. Check imports in server.py
    print("\n3️⃣ Checking server.py structure:")
    server_file = project_path / "server.py"
    if server_file.exists():
        content = server_file.read_text()
        
        # Check for required imports
        required_imports = [
            ("from fastmcp import FastMCP", "FastMCP framework"),
            ("from fastmcp.exceptions import ToolError", "Error handling"),
            ("@mcp.tool", "Tool decorators")
        ]
        
        for import_str, description in required_imports:
            if import_str in content:
                print(f"   ✅ Found: {import_str:<40} - {description}")
            else:
                print(f"   ❌ Missing: {import_str:<40} - {description}")
                all_valid = False
        
        # Count tools, resources, prompts
        tool_count = content.count("@mcp.tool")
        resource_count = content.count("@mcp.resource")
        prompt_count = content.count("@mcp.prompt")
        
        print(f"\n   📊 Components found:")
        print(f"      Tools: {tool_count}")
        print(f"      Resources: {resource_count}")
        print(f"      Prompts: {prompt_count}")
    
    # 4. Validate pyproject.toml
    print("\n4️⃣ Checking pyproject.toml:")
    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        if 'name = "' + project_name + '"' in content:
            print(f"   ✅ Project name correctly set to: {project_name}")
        else:
            print(f"   ❌ Project name mismatch")
            all_valid = False
            
        if 'dependencies = [' in content:
            # Extract dependencies
            start = content.find('dependencies = [')
            end = content.find(']', start)
            deps_str = content[start:end+1]
            print(f"   ✅ Dependencies section found")
            print(f"      {deps_str[:100]}...")
        else:
            print(f"   ❌ No dependencies section found")
            all_valid = False
    
    # 5. Run project validation
    print("\n5️⃣ Running comprehensive validation:")
    validation_result = validate_project(project_path)
    print(f"   Overall valid: {validation_result['valid']}")
    print(f"   Files checked: {validation_result['files_checked']}")
    
    if validation_result['issues']:
        print("   Issues found:")
        for issue in validation_result['issues']:
            print(f"      ❌ {issue}")
            all_valid = False
    
    if validation_result['warnings']:
        print("   Warnings:")
        for warning in validation_result['warnings']:
            print(f"      ⚠️  {warning}")
    
    return all_valid and validation_result['valid']


async def main():
    """Run the edge case tests"""
    print_section("KEN-MCP Edge Case Testing")
    print("Testing complex MCP generation with the refactored codebase")
    print(f"Output directory: {Path('test_edge_cases').absolute()}")
    
    # Clean up any previous test runs
    test_dir = Path("test_edge_cases")
    if test_dir.exists():
        print("\n🧹 Cleaning up previous test runs...")
        for item in ["system-monitor-mcp", "document-processor-mcp"]:
            path = test_dir / item
            if path.exists():
                shutil.rmtree(path)
                print(f"   Removed: {item}")
    
    # Edge Case 1: Multi-Modal System Monitor
    edge_case_1 = await generate_edge_case_mcp(
        name="Multi-Modal System Monitor",
        requirements="""Create an MCP that monitors system resources (CPU, memory, disk, network), 
        scrapes cryptocurrency prices from multiple APIs, stores time-series data in SQLite, 
        generates real-time alerts via webhooks when thresholds are exceeded, provides REST API 
        endpoints for historical data, WebSocket streaming for live updates, authentication with 
        JWT tokens, rate limiting per user, and interactive data visualization dashboards. 
        Include support for custom alert rules, data export in multiple formats, and integration 
        with monitoring services like Datadog and PagerDuty.""",
        project_name="system-monitor-mcp",
        dependencies=["psutil", "aiohttp", "websockets", "plotly", "jwt", "aiosqlite"]
    )
    
    # Edge Case 2: AI Document Intelligence Platform  
    edge_case_2 = await generate_edge_case_mcp(
        name="AI Document Intelligence Platform",
        requirements="""Build an MCP that processes documents in multiple formats (PDF with forms, 
        scanned images, Word with track changes, Excel with formulas, PowerPoint, emails with 
        attachments), performs OCR with multiple language support, extracts structured data using 
        transformer-based NLP models, classifies documents using fine-tuned BERT, manages complex 
        document workflows with parallel approval chains, integrates with S3, Google Drive, and 
        SharePoint, sends templated email notifications via SendGrid, provides GraphQL API with 
        real-time subscriptions, implements RBAC with OAuth2, maintains audit trails, and includes 
        document versioning with diff visualization.""",
        project_name="document-processor-mcp",
        dependencies=["pypdf2", "python-docx", "openpyxl", "pytesseract", "transformers", 
                     "boto3", "google-api-python-client", "sendgrid", "graphene"]
    )
    
    # Final Summary
    print_section("TEST SUMMARY")
    
    print("\n📊 Results:")
    print(f"   Edge Case 1 (System Monitor):     {'✅ PASSED' if edge_case_1 else '❌ FAILED'}")
    print(f"   Edge Case 2 (Document Processor): {'✅ PASSED' if edge_case_2 else '❌ FAILED'}")
    
    if edge_case_1 and edge_case_2:
        print("\n🎉 ALL TESTS PASSED!")
        print("The refactored KEN-MCP successfully generated complex MCPs with:")
        print("   ✅ No syntax errors")
        print("   ✅ Complete file structure")
        print("   ✅ Proper dependency detection")
        print("   ✅ Valid Python code")
        print("   ✅ Comprehensive documentation")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    # Show generated projects
    print("\n📁 Generated projects:")
    for project in ["system-monitor-mcp", "document-processor-mcp"]:
        project_path = test_dir / project
        if project_path.exists():
            print(f"   {project_path.absolute()}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())