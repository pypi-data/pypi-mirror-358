"""
CLAUDE.md generation for KEN-MCP
Generates comprehensive rules and context files for Claude Code
"""

from pathlib import Path

from ken_mcp.core.models import GenerationPlan


def generate_claude_md_file(project_path: Path, plan: GenerationPlan, project_name: str) -> None:
    """Generate CLAUDE.md with MCP rules and project context
    
    Args:
        project_path: Path to project directory
        plan: Generation plan with project details
        project_name: Name of the project
    """
    from ken_mcp.templates.constants import CLAUDE_MD_TEMPLATE
    
    # Extract tool and resource information
    tool_names = [tool.name for tool in plan.tools]
    
    # Extract concise descriptions (just the first line before "Domain:")
    tool_descriptions = []
    for tool in plan.tools:
        # Get the first line which should be the concise description
        first_line = tool.description.split('\n')[0].strip()
        tool_descriptions.append(f"- **{tool.name}**: {first_line}")
    
    
    resource_names = [resource.uri_pattern for resource in plan.resources]
    
    # Extract concise resource descriptions  
    resource_descriptions = []
    for resource in plan.resources:
        # Resources usually have shorter descriptions, but still clean them up
        clean_desc = resource.description.split('\n')[0].strip()
        resource_descriptions.append(f"- **{resource.uri_pattern}**: {clean_desc}")
    
    # Get version from pyproject.toml
    from ken_mcp import __version__
    
    claude_md_content = CLAUDE_MD_TEMPLATE.format(
        project_name=project_name,
        requirements=plan.original_requirements,
        description=plan.description or f"MCP server for {project_name}",
        tool_count=len(plan.tools),
        resource_count=len(plan.resources),
        tools_list="\n".join(tool_descriptions) if tool_descriptions else "- No tools defined",
        resources_list="\n".join(resource_descriptions) if resource_descriptions else "- No resources defined",
        tool_names=", ".join(tool_names) if tool_names else "none",
        resource_names=", ".join(resource_names) if resource_names else "none",
        version=__version__
    )
    
    # Generate CLAUDE.md in the parent directory (root of codebase)
    claude_md_file = project_path.parent / "CLAUDE.md"
    claude_md_file.write_text(claude_md_content)
    
    # Make readable (not executable)
    claude_md_file.chmod(0o644)