"""
Validation utilities for KEN-MCP generator
Handles project validation, syntax checking, and file verification
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import ast


def validate_project(project_path: Path) -> Dict[str, Any]:
    """Validate the generated project structure and files
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        Validation results dictionary
    """
    issues = []
    warnings = []
    
    # Check required files
    required_files = [
        "server.py", 
        "README.md", 
        "help.md", 
        "test.py", 
        "pyproject.toml", 
        ".gitignore"
    ]
    
    for file in required_files:
        if not (project_path / file).exists():
            issues.append(f"Missing required file: {file}")
    
    # Check Python syntax in server.py
    server_file = project_path / "server.py"
    if server_file.exists():
        syntax_error = check_python_syntax(server_file)
        if syntax_error:
            issues.append(f"Syntax error in server.py: {syntax_error}")
    
    # Check test file syntax
    test_file = project_path / "test.py"
    if test_file.exists():
        syntax_error = check_python_syntax(test_file)
        if syntax_error:
            issues.append(f"Syntax error in test.py: {syntax_error}")
    
    # Check if files are executable
    for py_file in ["server.py", "test.py"]:
        file_path = project_path / py_file
        if file_path.exists() and not file_path.stat().st_mode & 0o111:
            warnings.append(f"{py_file} is not executable")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "files_checked": len(required_files)
    }


def check_python_syntax(file_path: Path) -> Optional[str]:
    """Check Python file for syntax errors
    
    Args:
        file_path: Path to Python file
        
    Returns:
        Error message if syntax error found, None otherwise
    """
    try:
        content = file_path.read_text()
        ast.parse(content)
        return None
    except SyntaxError as e:
        return f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return str(e)


def validate_parameter_count(params: List[Dict[str, Any]], max_params: int = 4) -> Optional[str]:
    """Validate function parameter count according to CLAUDE.md rules
    
    Args:
        params: List of parameter definitions
        max_params: Maximum allowed parameters
        
    Returns:
        Error message if too many params, None otherwise
    """
    # Don't count ctx parameter
    non_ctx_params = [p for p in params if p.get("name") != "ctx"]
    
    if len(non_ctx_params) > max_params:
        return f"Too many parameters ({len(non_ctx_params)}), maximum is {max_params}"
    return None


def validate_imports(imports: List[str], stdlib_modules: set) -> Dict[str, List[str]]:
    """Separate standard library imports from external dependencies
    
    Args:
        imports: List of import statements
        stdlib_modules: Set of standard library module names
        
    Returns:
        Dictionary with 'stdlib' and 'external' lists
    """
    stdlib = []
    external = []
    
    for imp in imports:
        # Extract module name from import statement
        module_name = imp.split()[1] if imp.startswith("from") else imp.split()[1]
        module_name = module_name.split('.')[0]  # Get root module
        
        if module_name in stdlib_modules:
            stdlib.append(imp)
        else:
            external.append(imp)
    
    return {
        "stdlib": stdlib,
        "external": external
    }


def validate_file_path(path: str) -> bool:
    """Check if a file path is valid and safe
    
    Args:
        path: File path to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check for path traversal attempts
        if ".." in path or path.startswith("/"):
            return False
        
        # Try to create a Path object
        Path(path)
        return True
    except Exception:
        return False


def validate_url(url: str) -> bool:
    """Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    return url.startswith("http://") or url.startswith("https://")


def validate_tool_definition(tool: Dict[str, Any]) -> List[str]:
    """Validate a tool definition structure
    
    Args:
        tool: Tool definition dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    if "name" not in tool:
        errors.append("Tool missing 'name' field")
    elif not tool["name"] or not isinstance(tool["name"], str):
        errors.append("Tool name must be a non-empty string")
    
    if "description" not in tool:
        errors.append("Tool missing 'description' field")
    
    # Validate parameters if present
    if "parameters" in tool:
        if not isinstance(tool["parameters"], list):
            errors.append("Tool parameters must be a list")
        else:
            for i, param in enumerate(tool["parameters"]):
                if not isinstance(param, dict):
                    errors.append(f"Parameter {i} must be a dictionary")
                elif "name" not in param:
                    errors.append(f"Parameter {i} missing 'name' field")
                elif "type" not in param:
                    errors.append(f"Parameter {param.get('name', i)} missing 'type' field")
    
    return errors


def validate_project_name(name: str) -> Optional[str]:
    """Validate project name
    
    Args:
        name: Project name to validate
        
    Returns:
        Error message if invalid, None otherwise
    """
    if not name:
        return "Project name cannot be empty"
    
    if len(name) > 50:
        return "Project name too long (max 50 characters)"
    
    # Check for valid characters
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return "Project name can only contain letters, numbers, hyphens, and underscores"
    
    return None