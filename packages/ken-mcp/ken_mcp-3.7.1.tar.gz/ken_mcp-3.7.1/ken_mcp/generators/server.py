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
    RESOURCE_TEMPLATE, PROMPT_TEMPLATE, DATE_FORMAT,
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
    """Generate server.py and requirements.txt files
    
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
    
    # Generate requirements.txt instead of pyproject.toml
    requirements_content = generate_requirements(
        plan, 
        additional_dependencies
    )
    (project_path / "requirements.txt").write_text(requirements_content)


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
    
    # Add analysis context if available
    analysis_comment = ""
    if hasattr(plan, 'analysis_context') and plan.analysis_context:
        analysis_comment = f"""
Analysis Results:
- Domain: {plan.analysis_context.get('domain', 'general')}
- Primary actions: {', '.join(plan.analysis_context.get('primary_actions', []))}
- Key entities: {', '.join(plan.analysis_context.get('entities', []))}
- Operations: {', '.join(plan.analysis_context.get('operations', []))}
"""
    
    # Format header
    server_code = SERVER_HEADER_TEMPLATE.format(
        description=plan.description,
        date=datetime.now().strftime(DATE_FORMAT),
        requirements=escape_for_docstring(plan.original_requirements + analysis_comment),
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
        "import os",
        "import sys",
        "import logging"
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
    elif tool.implementation == "intelligent":
        implementation = generate_intelligent_implementation(tool)
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


def generate_intelligent_implementation(tool: ToolDefinition) -> str:
    """Generate intelligent implementation stub for a tool
    
    Args:
        tool: Tool definition
        
    Returns:
        Implementation code with rich context
    """
    # Extract tool type from name or description
    tool_name_lower = tool.name.lower()
    
    # Generate appropriate implementation based on tool type
    if any(action in tool_name_lower for action in ['create', 'add', 'new']):
        return f'''    # Implementation for creating/adding
    try:
        await ctx.info(f"Creating new item...")
        
        # TODO: Validate input data
        # TODO: Create the resource
        # TODO: Return created item with ID
        
        return {{
            "status": "success",
            "message": f"Created successfully",
            "id": "generated-id",
            "data": {{}}
        }}
    except Exception as e:
        raise ToolError(f"Failed to create: {{e}}")'''
    
    elif any(action in tool_name_lower for action in ['list', 'get_all', 'fetch_all']):
        return f'''    # Implementation for listing/fetching multiple items
    try:
        await ctx.info(f"Fetching items...")
        
        # TODO: Apply filters if provided
        # TODO: Implement pagination
        # TODO: Fetch from data source
        
        items = []  # TODO: Fetch actual items
        
        return {{
            "status": "success",
            "count": len(items),
            "items": items,
            "total": len(items)
        }}
    except Exception as e:
        raise ToolError(f"Failed to list items: {{e}}")'''
    
    elif any(action in tool_name_lower for action in ['get', 'fetch', 'retrieve']):
        return f'''    # Implementation for getting a specific item
    try:
        await ctx.info(f"Fetching item...")
        
        # TODO: Validate ID format
        # TODO: Fetch from data source
        # TODO: Handle not found case
        
        item = {{}}  # TODO: Fetch actual item
        
        if not item:
            raise ToolError("Item not found")
            
        return {{
            "status": "success",
            "data": item
        }}
    except Exception as e:
        raise ToolError(f"Failed to get item: {{e}}")'''
    
    elif any(action in tool_name_lower for action in ['update', 'edit', 'modify']):
        return f'''    # Implementation for updating
    try:
        await ctx.info(f"Updating item...")
        
        # TODO: Validate ID and updates
        # TODO: Fetch existing item
        # TODO: Apply updates
        # TODO: Save changes
        
        return {{
            "status": "success",
            "message": "Updated successfully",
            "data": {{}}
        }}
    except Exception as e:
        raise ToolError(f"Failed to update: {{e}}")'''
    
    elif any(action in tool_name_lower for action in ['delete', 'remove']):
        return f'''    # Implementation for deletion
    try:
        if not confirm:
            raise ToolError("Deletion requires confirmation")
            
        await ctx.info(f"Deleting item...")
        
        # TODO: Validate ID
        # TODO: Check if item exists
        # TODO: Perform deletion
        
        return {{
            "status": "success",
            "message": "Deleted successfully"
        }}
    except Exception as e:
        raise ToolError(f"Failed to delete: {{e}}")'''
    
    elif any(action in tool_name_lower for action in ['process', 'analyze', 'transform']):
        return f'''    # Implementation for processing/analysis
    try:
        await ctx.info(f"Processing data...")
        
        # TODO: Validate input data
        # TODO: Perform processing/analysis
        # TODO: Return results
        
        results = {{}}  # TODO: Process actual data
        
        return {{
            "status": "success",
            "results": results
        }}
    except Exception as e:
        raise ToolError(f"Failed to process: {{e}}")'''
    
    elif any(action in tool_name_lower for action in ['monitor', 'watch', 'track']):
        return f'''    # Implementation for monitoring
    try:
        await ctx.info(f"Starting monitoring...")
        
        # TODO: Set up monitoring parameters
        # TODO: Check current status
        # TODO: Compare with thresholds
        
        status = {{}}  # TODO: Get actual status
        
        return {{
            "status": "success",
            "monitoring": True,
            "current_status": status
        }}
    except Exception as e:
        raise ToolError(f"Failed to monitor: {{e}}")'''
    
    else:
        # Generic implementation
        return generate_boilerplate_implementation(tool)


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
    resource_name = resource.uri_pattern.split("://")[1].replace("/", "_").replace("{", "").replace("}", "").replace(" ", "_")
    escaped_desc = escape_for_docstring(resource.description)
    
    # Extract parameters from URI pattern (e.g., {id} -> id: str)
    import re
    uri_params = re.findall(r'\{(\w+)\}', resource.uri_pattern)
    params_str = ", ".join(f"{param}: str" for param in uri_params) if uri_params else ""
    
    return RESOURCE_TEMPLATE.format(
        uri=resource.uri_pattern,
        resource_name=resource_name,
        description=escaped_desc,
        params_str=params_str
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


def generate_requirements(
    plan: GenerationPlan,
    additional_dependencies: Optional[List[str]] = None
) -> str:
    """Generate requirements.txt content
    
    Args:
        plan: Generation plan
        additional_dependencies: Extra dependencies
        
    Returns:
        requirements.txt content
    """
    dependencies = ["fastmcp>=0.1.0"]
    
    # Add dependencies from plan (excluding standard library)
    for dep in plan.dependencies:
        if dep not in STDLIB_MODULES and dep not in dependencies:
            dependencies.append(dep)
    
    # Add additional dependencies
    if additional_dependencies:
        for dep in additional_dependencies:
            if dep not in dependencies:
                dependencies.append(dep)
    
    # Add environment support if needed
    if categorize_requirement(plan.original_requirements).get("needs_env", False):
        if "python-dotenv" not in dependencies:
            dependencies.append("python-dotenv")
    
    # Add suggested dependencies
    suggested = suggest_dependencies(plan.original_requirements)
    for dep in suggested:
        if dep not in dependencies:
            dependencies.append(dep)
    
    # Return as simple requirements.txt format
    return "\n".join(dependencies) + "\n"