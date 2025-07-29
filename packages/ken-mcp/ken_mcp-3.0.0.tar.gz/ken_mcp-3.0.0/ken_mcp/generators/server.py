"""
Server code generator for KEN-MCP
Handles generation of server.py and pyproject.toml files
"""

from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

from ken_mcp.core.models import GenerationPlan, ToolDefinition, ResourceDefinition, PromptDefinition
from ken_mcp.templates.constants import (
    SERVER_HEADER_TEMPLATE, TOOL_BOILERPLATE_TEMPLATE, TOOL_FALLBACK_TEMPLATE,
    RESOURCE_TEMPLATE, PROMPT_TEMPLATE, PYPROJECT_TEMPLATE, DATE_FORMAT,
    STDLIB_MODULES
)
from ken_mcp.utils.text import escape_for_docstring, format_json_string
from ken_mcp.utils.suggestions import suggest_dependencies, categorize_requirement
from ken_mcp.generators.project import make_executable


def generate_server_code(
    project_path: Path, 
    plan: GenerationPlan,
    python_version: str = "3.10",
    additional_dependencies: Optional[List[str]] = None
) -> None:
    """Generate server.py and pyproject.toml files
    
    Args:
        project_path: Path to project directory
        plan: Generation plan with tools, resources, etc.
        python_version: Minimum Python version
        additional_dependencies: Extra dependencies to include
    """
    # Generate server.py
    server_code = generate_server_python(plan, project_path.name, python_version)
    server_path = project_path / "server.py"
    server_path.write_text(server_code)
    make_executable(server_path)
    
    # Generate pyproject.toml
    pyproject_content = generate_pyproject(
        project_path.name, 
        plan, 
        python_version, 
        additional_dependencies
    )
    (project_path / "pyproject.toml").write_text(pyproject_content)


def generate_server_python(plan: GenerationPlan, project_name: str, python_version: str) -> str:
    """Generate the server.py content
    
    Args:
        plan: Generation plan
        project_name: Name of the project
        python_version: Python version requirement
        
    Returns:
        Generated Python code
    """
    # Build imports
    imports = build_imports(plan)
    
    # Check if environment loading is needed
    needs_env = categorize_requirement(plan.original_requirements).get("needs_env", False)
    env_loading = "# Load environment variables\nload_dotenv()\n\n" if needs_env else ""
    
    # Format header
    server_code = SERVER_HEADER_TEMPLATE.format(
        description=plan.description,
        date=datetime.now().strftime(DATE_FORMAT),
        requirements=escape_for_docstring(plan.original_requirements),
        imports="\n".join(imports),
        env_loading=env_loading,
        project_name=project_name
    )
    
    # Add tools
    for tool in plan.tools:
        server_code += generate_tool_code(tool)
    
    # Add resources
    if plan.resources:
        server_code += "\n# Resources - TODO: Claude, implement these based on requirements\n"
        for resource in plan.resources:
            server_code += generate_resource_code(resource)
    
    # Add prompts
    if plan.prompts:
        server_code += "\n# Prompts - TODO: Claude, implement these based on requirements\n"
        for prompt in plan.prompts:
            server_code += generate_prompt_code(prompt)
    
    # Add main block
    server_code += '''

if __name__ == "__main__":
    mcp.run()
'''
    
    return server_code


def build_imports(plan: GenerationPlan) -> List[str]:
    """Build import statements based on plan requirements
    
    Args:
        plan: Generation plan
        
    Returns:
        List of import statements
    """
    imports = [
        "from fastmcp import FastMCP, Context",
        "from fastmcp.exceptions import ToolError", 
        "from typing import Dict, List, Any, Optional",
        "from pathlib import Path",
        "import json",
        "import os"
    ]
    
    # Check if we need environment variables
    requirements = plan.original_requirements
    needs_env = categorize_requirement(requirements).get("needs_env", False)
    if needs_env:
        imports.append("from dotenv import load_dotenv")
    
    return imports


def generate_tool_code(tool: ToolDefinition) -> str:
    """Generate code for a single tool
    
    Args:
        tool: Tool definition
        
    Returns:
        Generated tool code
    """
    # Build parameter list
    params_str = build_parameter_list(tool.parameters)
    
    # Generate implementation
    if tool.implementation == "boilerplate":
        implementation = generate_boilerplate_implementation(tool)
    else:
        implementation = generate_fallback_implementation(tool)
    
    # Escape description
    escaped_description = escape_for_docstring(tool.description)
    
    return f'''
@mcp.tool
async def {tool.name}(
    ctx: Context,
{params_str}
) -> Dict[str, Any]:
    """{escaped_description}"""
{implementation}
'''


def build_parameter_list(parameters: List) -> str:
    """Build formatted parameter list for function signature
    
    Args:
        parameters: List of parameter definitions
        
    Returns:
        Formatted parameter string
    """
    params = []
    param_defaults = []
    
    for param in parameters:
        p_name = param.name
        p_type = param.type
        p_default = param.default if hasattr(param, 'default') else None
        
        if p_default is not None:
            if p_default == "None" or p_type.startswith("Optional"):
                param_defaults.append(f"    {p_name}: {p_type} = None,")
            elif isinstance(p_default, str) and p_default != "None":
                param_defaults.append(f"    {p_name}: {p_type} = \"{p_default}\",")
            else:
                param_defaults.append(f"    {p_name}: {p_type} = {p_default},")
        else:
            params.append(f"    {p_name}: {p_type},")
    
    # Parameters with no defaults first, then those with defaults
    all_params = params + param_defaults
    params_str = "\n".join(all_params) if all_params else ""
    
    # Remove trailing comma if exists
    if params_str and params_str.endswith(','):
        params_str = params_str[:-1]
    
    return params_str


def generate_boilerplate_implementation(tool: ToolDefinition) -> str:
    """Generate boilerplate implementation for a tool
    
    Args:
        tool: Tool definition
        
    Returns:
        Implementation code
    """
    tool_desc = format_json_string(tool.description)
    return TOOL_BOILERPLATE_TEMPLATE.format(
        tool_name=tool.name,
        tool_desc=tool_desc
    )


def generate_fallback_implementation(tool: ToolDefinition) -> str:
    """Generate fallback implementation for a tool
    
    Args:
        tool: Tool definition
        
    Returns:
        Implementation code
    """
    tool_desc = format_json_string(tool.description)
    
    # Generate parameter validation
    param_validation = generate_parameter_validation(tool.parameters)
    
    return TOOL_FALLBACK_TEMPLATE.format(
        tool_name=tool.name,
        tool_desc=tool_desc,
        param_validation=param_validation
    )


def generate_parameter_validation(parameters: List) -> str:
    """Generate parameter validation code
    
    Args:
        parameters: List of parameter definitions
        
    Returns:
        Validation code
    """
    validation = ""
    for param in parameters:
        param_name = param.name
        param_type = param.type
        
        if param_type == "str" and "url" in param_name.lower():
            validation += f'''
        # Validate {param_name}
        if not {param_name} or not isinstance({param_name}, str):
            raise ToolError(f"Invalid {param_name}: must be a valid string")
        
        if "{param_name}" == "url" and not ({param_name}.startswith("http://") or {param_name}.startswith("https://")):
            raise ToolError(f"Invalid URL: {{{param_name}}} must start with http:// or https://")
'''
    
    return validation


def generate_resource_code(resource: ResourceDefinition) -> str:
    """Generate code for a resource
    
    Args:
        resource: Resource definition
        
    Returns:
        Generated resource code
    """
    resource_name = resource.uri_pattern.split("://")[1].replace("/", "_").replace("{", "").replace("}", "")
    escaped_desc = escape_for_docstring(resource.description)
    
    return RESOURCE_TEMPLATE.format(
        uri=resource.uri_pattern,
        resource_name=resource_name,
        description=escaped_desc
    )


def generate_prompt_code(prompt: PromptDefinition) -> str:
    """Generate code for a prompt
    
    Args:
        prompt: Prompt definition
        
    Returns:
        Generated prompt code
    """
    # Build prompt parameters
    prompt_params = []
    for param in prompt.parameters:
        p_name = param.name
        p_type = param.type
        p_default = param.default if hasattr(param, 'default') else None
        
        if p_default is not None:
            prompt_params.append(f"{p_name}: {p_type} = {repr(p_default)}")
        else:
            prompt_params.append(f"{p_name}: {p_type}")
    
    params_str = ", ".join(prompt_params)
    escaped_desc = escape_for_docstring(prompt.description)
    
    return PROMPT_TEMPLATE.format(
        prompt_name=prompt.name,
        params_str=params_str,
        description=escaped_desc
    )


def generate_pyproject(
    project_name: str,
    plan: GenerationPlan,
    python_version: str,
    additional_dependencies: Optional[List[str]] = None
) -> str:
    """Generate pyproject.toml content
    
    Args:
        project_name: Name of the project
        plan: Generation plan
        python_version: Python version requirement
        additional_dependencies: Extra dependencies
        
    Returns:
        pyproject.toml content
    """
    dependencies = ["fastmcp>=0.1.0"]
    
    # Add dependencies from plan (excluding standard library)
    for dep in plan.dependencies:
        if dep not in STDLIB_MODULES and dep not in dependencies:
            dependencies.append(dep)
    
    # Add additional dependencies
    if additional_dependencies:
        dependencies.extend(additional_dependencies)
    
    # Add environment support if needed
    if categorize_requirement(plan.original_requirements).get("needs_env", False):
        if "python-dotenv" not in dependencies:
            dependencies.append("python-dotenv")
    
    # Add suggested dependencies
    suggested = suggest_dependencies(plan.original_requirements)
    for dep in suggested:
        if dep not in dependencies:
            dependencies.append(dep)
    
    return PYPROJECT_TEMPLATE.format(
        project_name=project_name,
        description=plan.description,
        python_version=python_version,
        dependencies=format_json_string(dependencies)
    )