#!/usr/bin/env python3
"""
Direct test of refactored modules without fastmcp dependency
"""

import sys
import asyncio
from pathlib import Path
import importlib.util

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock fastmcp before any imports
class MockContext:
    async def info(self, msg):
        print(f"[INFO] {msg}")
    
    async def report_progress(self, current, total, msg):
        print(f"[PROGRESS {current}/{total}] {msg}")

class MockToolError(Exception):
    pass

fastmcp_mock = type(sys)('fastmcp')
fastmcp_mock.Context = MockContext
fastmcp_mock.exceptions = type(sys)('exceptions')
fastmcp_mock.exceptions.ToolError = MockToolError

sys.modules['fastmcp'] = fastmcp_mock
sys.modules['fastmcp.exceptions'] = fastmcp_mock.exceptions

# Import modules directly to avoid __init__.py
def import_module_directly(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import the modules we need
base_path = Path(__file__).parent.parent / "ken_mcp"
models = import_module_directly("models", base_path / "core" / "models.py")
orchestrator = import_module_directly("orchestrator", base_path / "core" / "orchestrator.py")
validation = import_module_directly("validation", base_path / "utils" / "validation.py")

# Import classes we need
ProjectConfig = models.ProjectConfig
validate_project = validation.validate_project

# Mock the imports that orchestrator needs
sys.modules['ken_mcp.core.models'] = models
sys.modules['ken_mcp.utils.validation'] = validation

# Mock other dependencies
analyzer = import_module_directly("analyzer", base_path / "core" / "analyzer.py")
project = import_module_directly("project", base_path / "generators" / "project.py")
server = import_module_directly("server", base_path / "generators" / "server.py")
docs = import_module_directly("docs", base_path / "generators" / "docs.py")
tests = import_module_directly("tests", base_path / "generators" / "tests.py")
text = import_module_directly("text", base_path / "utils" / "text.py")
suggestions = import_module_directly("suggestions", base_path / "utils" / "suggestions.py")

# Set up all the module dependencies
sys.modules['ken_mcp.core.analyzer'] = analyzer
sys.modules['ken_mcp.generators.project'] = project
sys.modules['ken_mcp.generators.server'] = server
sys.modules['ken_mcp.generators.docs'] = docs
sys.modules['ken_mcp.generators.tests'] = tests
sys.modules['ken_mcp.utils.text'] = text
sys.modules['ken_mcp.utils.suggestions'] = suggestions

# Mock constants
constants = type(sys)('constants')
constants.MAX_DOCSTRING_LENGTH = 500
constants.GITIGNORE_TEMPLATE = "__pycache__/\\n*.pyc\\n.env\\nvenv/\\n"
constants.ENV_EXAMPLE_TEMPLATE = "# Environment variables\\n"
constants.DOMAIN_KEYWORDS = {
    "monitoring": ["monitor", "track", "watch", "alert"],
    "api_integration": ["api", "endpoint", "rest", "http"],
    "database": ["database", "sql", "query", "table"],
    "web_scraping": ["scrape", "web", "html", "crawl"],
    "ml_ai": ["classify", "predict", "analyze", "nlp"],
    "file_processing": ["file", "document", "pdf", "csv"],
}
constants.DEPENDENCY_SUGGESTIONS = {
    "api_http": ["httpx", "requests"],
    "web_scraping": ["beautifulsoup4", "requests", "lxml"],
    "database": ["sqlalchemy", "psycopg2", "pymysql"],
    "websocket": ["websockets", "asyncio"],
    "ml_ai": ["scikit-learn", "nltk", "spacy"],
    "pdf": ["pypdf2"],
    "image": ["pillow"],
}
constants.DEFAULT_TOOL_NAMES = {
    0: {"default": ["create_item", "add_entry", "initialize"]},
    1: {"default": ["list_items", "search_data", "query_items"]},
    2: {"default": ["update_item", "process_data", "modify_entry"]}
}
constants.LOG_MESSAGES = {
    "starting_generation": "Starting MCP generation for: {project_name}",
    "analyzing_requirements": "Analyzing requirements...",
    "creating_project": "Creating project structure...",
    "generating_code": "Generating server code...",
    "generating_docs": "Generating documentation...",
    "generating_tests": "Generating test suite...",
    "validating_project": "Validating project...",
    "project_created": "Created project at: {project_path}",
    "plan_created": "Plan created with {tool_count} tools",
    "server_generated": "Generated server.py and pyproject.toml",
    "docs_generated": "Generated documentation files",
    "tests_generated": "Generated test.py with comprehensive test suite"
}
constants.PROGRESS_MESSAGES = {
    "analyzing": "Analyzing requirements...",
    "creating_structure": "Creating project structure...",
    "generating_server": "Generating server code...",
    "creating_docs": "Creating documentation...",
    "generating_tests": "Generating test suite...",
    "validating": "Validating project...",
    "complete": "Generation complete!"
}

# Import all template constants
import json
exec(open(base_path / "templates" / "constants.py").read(), constants.__dict__)

sys.modules['ken_mcp.templates.constants'] = constants

# Mock Context
class MockContext:
    async def info(self, msg):
        print(f"[INFO] {msg}")
    
    async def report_progress(self, current, total, msg):
        print(f"[PROGRESS {current}/{total}] {msg}")

# Now we can use the orchestrator
generate_mcp_server = orchestrator.generate_mcp_server


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