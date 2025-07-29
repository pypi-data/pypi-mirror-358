#!/usr/bin/env python3.10
"""
KEN-MCP: Universal MCP Server Generator
Generates MCP servers for ANY purpose based on natural language requirements
"""

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from pydantic import Field
from typing import Annotated, Optional, List, Dict, Any
from pathlib import Path

from ken_mcp.core.models import ProjectConfig
from ken_mcp.core.orchestrator import generate_mcp_server as orchestrate_generation
from ken_mcp.core.analyzer import analyze_and_plan
from ken_mcp.utils.validation import validate_project

# Initialize the MCP server
mcp = FastMCP(name="KEN-MCP 🏗️")


@mcp.tool
async def generate_mcp_server(
    ctx: Context,
    requirements: Annotated[str, Field(description="Natural language description of desired MCP functionality")],
    project_name: Annotated[str, Field(description="Name for the MCP project (e.g., 'todo-manager')")],
    output_dir: Annotated[Optional[str], Field(description="Directory to create the project in")] = None,
    include_resources: Annotated[bool, Field(description="Whether to include MCP resources")] = True,
    include_prompts: Annotated[bool, Field(description="Whether to include MCP prompts")] = True,
    python_version: Annotated[str, Field(description="Minimum Python version required")] = "3.10",
    additional_dependencies: Annotated[Optional[List[str]], Field(description="Additional Python packages to include")] = None
) -> Dict[str, Any]:
    """Generate a complete MCP server from requirements. Works for ANY type of MCP - not just APIs!
    
    Examples:
    - "I want an MCP that manages todo lists"
    - "Create an MCP for tracking my daily habits" 
    - "Build an MCP that can analyze text files"
    - "I need an MCP that interfaces with YouTube API"
    """
    try:
        # Create configuration object (max 4 params per function as per CLAUDE.md)
        config = ProjectConfig(
            requirements=requirements,
            project_name=project_name,
            output_dir=output_dir,
            include_resources=include_resources,
            include_prompts=include_prompts,
            python_version=python_version,
            additional_dependencies=additional_dependencies
        )
        
        # Use orchestrator to generate the server
        result = await orchestrate_generation(ctx, config)
        
        if not result.success:
            raise ToolError(result.error or "Failed to generate MCP server")
        
        return result.to_dict()
        
    except Exception as e:
        raise ToolError(f"Failed to generate MCP server: {str(e)}")


@mcp.tool
async def analyze_requirements(
    ctx: Context,
    requirements: Annotated[str, Field(description="Natural language description to analyze")]
) -> Dict[str, Any]:
    """Analyze requirements and suggest an implementation plan without generating code"""
    await ctx.info("🔍 Analyzing requirements...")
    
    try:
        plan = analyze_and_plan(requirements)
        
        return {
            "description": plan.description,
            "suggested_tools": len(plan.tools),
            "suggested_resources": len(plan.resources),
            "suggested_prompts": len(plan.prompts),
            "dependencies": plan.dependencies,
            "plan_details": plan.to_dict()
        }
    except Exception as e:
        raise ToolError(f"Failed to analyze requirements: {str(e)}")


@mcp.tool
async def list_generated_servers(
    ctx: Context,
    directory: Annotated[Optional[str], Field(description="Directory to search in")] = None
) -> List[Dict[str, Any]]:
    """List all previously generated MCP servers"""
    await ctx.info("📋 Listing generated servers...")
    
    try:
        search_dir = Path(directory) if directory else Path.cwd()
        servers = []
        
        if search_dir.exists():
            for project_dir in search_dir.iterdir():
                if project_dir.is_dir() and (project_dir / "server.py").exists():
                    try:
                        # Check for validation
                        validation = validate_project(project_dir)
                        
                        # Try to get description
                        help_path = project_dir / "help.md"
                        readme_path = project_dir / "README.md"
                        description = "No description available"
                        
                        desc_file = help_path if help_path.exists() else readme_path
                        if desc_file.exists():
                            lines = desc_file.read_text().split('\n')
                            for line in lines[1:10]:
                                if line.strip() and not line.startswith('#'):
                                    description = line.strip()
                                    break
                        
                        servers.append({
                            "name": project_dir.name,
                            "path": str(project_dir),
                            "description": description,
                            "valid": validation["valid"],
                            "issues": validation.get("issues", []),
                            "created": project_dir.stat().st_ctime
                        })
                    except Exception:
                        pass
        
        # Sort by creation time
        servers.sort(key=lambda x: x["created"], reverse=True)
        
        # Format timestamps
        from datetime import datetime
        for server in servers:
            server["created"] = datetime.fromtimestamp(server["created"]).isoformat()
        
        return servers
        
    except Exception as e:
        raise ToolError(f"Failed to list servers: {str(e)}")


if __name__ == "__main__":
    mcp.run()