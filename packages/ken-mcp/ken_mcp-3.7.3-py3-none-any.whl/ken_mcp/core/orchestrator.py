"""
MCP generation orchestrator for KEN-MCP
Coordinates all generation steps and handles errors
"""

from pathlib import Path
from typing import List
from fastmcp import Context
from fastmcp.exceptions import ToolError

from ken_mcp.core.models import ProjectConfig, GenerationResult, GenerationPlan
from ken_mcp.core.analyzer import analyze_and_plan
from ken_mcp.generators.project import create_project_structure, create_diagnostic_script, create_wrapper_script
from ken_mcp.generators.server import generate_server_code
from ken_mcp.generators.docs import generate_documentation
from ken_mcp.generators.tests import generate_test_file
from ken_mcp.utils.validation import validate_project
from ken_mcp.templates.constants import LOG_MESSAGES, PROGRESS_MESSAGES


async def generate_mcp_server(
    ctx: Context,
    config: ProjectConfig
) -> GenerationResult:
    """Generate a complete MCP server from configuration
    
    Args:
        ctx: FastMCP context for logging and progress
        config: Project configuration
        
    Returns:
        Generation result with status and details
        
    Raises:
        ToolError: If generation fails
    """
    await ctx.info(LOG_MESSAGES["starting_generation"].format(project_name=config.project_name))
    
    try:
        # Validate configuration
        validation_errors = config.validate()
        if validation_errors:
            raise ToolError(f"Invalid configuration: {'; '.join(validation_errors)}")
        
        # Step 1: Analyze requirements and plan
        await ctx.report_progress(10, 100, PROGRESS_MESSAGES["analyzing"])
        plan = await analyze_requirements(config, ctx)
        
        # Step 2: Create project structure
        await ctx.report_progress(30, 100, PROGRESS_MESSAGES["creating_structure"])
        project_path = await create_structure(config, ctx)
        
        # Step 3: Generate server code
        await ctx.report_progress(50, 100, PROGRESS_MESSAGES["generating_server"])
        await generate_code(project_path, plan, config, ctx)
        
        # Step 4: Generate documentation
        await ctx.report_progress(70, 100, PROGRESS_MESSAGES["creating_docs"])
        await generate_docs(project_path, plan, config, ctx)
        
        # Step 4.1: Generate help.md in root directory
        await generate_help_docs(project_path.parent, project_path, plan, config, ctx)
        
        # Step 4.2: Generate README.md in root directory
        await generate_readme_docs(project_path.parent, plan, config, ctx)
        
        # Step 5: Create scripts directory for development tools
        scripts_path = project_path.parent / "scripts"
        scripts_path.mkdir(exist_ok=True)
        
        # Step 5.1: Generate test suite (in scripts/)
        await ctx.report_progress(80, 100, PROGRESS_MESSAGES["generating_tests"])
        await generate_tests_to_scripts(scripts_path, project_path, plan, config, ctx)
        
        # Step 5.2: Generate diagnostic script (in scripts/)
        create_diagnostic_script_to_scripts(scripts_path, project_path, config.project_name, config.python_version)
        create_wrapper_script(project_path, config.python_version)
        
        # Step 5.3: Generate verification script (in scripts/)
        from ken_mcp.generators.verification import generate_verification_file_to_scripts
        generate_verification_file_to_scripts(scripts_path, project_path, plan, config.project_name)
        
        # Step 5.7: Generate CLAUDE.md rules file
        from ken_mcp.generators.claude_md import generate_claude_md_file
        generate_claude_md_file(project_path, plan, config.project_name)
        
        # Step 6: Validate project
        await ctx.report_progress(90, 100, PROGRESS_MESSAGES["validating"])
        validation_result = await validate_generated_project(project_path, ctx)
        
        await ctx.report_progress(100, 100, PROGRESS_MESSAGES["complete"])
        
        # Build result
        return GenerationResult(
            success=True,
            project_path=project_path,
            project_name=config.project_name,
            tools_generated=len(plan.tools),
            resources_generated=len(plan.resources),
            prompts_generated=len(plan.prompts),
            validation=validation_result,
            next_steps=generate_next_steps(project_path)
        )
        
    except Exception as e:
        return GenerationResult(
            success=False,
            project_path=Path("."),
            project_name=config.project_name,
            error=str(e)
        )


async def analyze_requirements(config: ProjectConfig, ctx: Context) -> GenerationPlan:
    """Analyze requirements and create generation plan
    
    Args:
        config: Project configuration
        ctx: FastMCP context
        
    Returns:
        Generation plan
    """
    await ctx.info(LOG_MESSAGES["analyzing_requirements"])
    
    plan = analyze_and_plan(
        config.requirements,
        include_resources=config.include_resources,
        include_prompts=config.include_prompts
    )
    
    await ctx.info(LOG_MESSAGES["plan_created"].format(tool_count=len(plan.tools)))
    return plan


async def create_structure(config: ProjectConfig, ctx: Context) -> Path:
    """Create project directory structure
    
    Args:
        config: Project configuration
        ctx: FastMCP context
        
    Returns:
        Path to created project
    """
    await ctx.info(LOG_MESSAGES["creating_project"])
    
    project_path = create_project_structure(
        config.project_name,
        config.output_dir
    )
    
    await ctx.info(LOG_MESSAGES["project_created"].format(project_path=project_path))
    return project_path


async def generate_code(
    project_path: Path, 
    plan: GenerationPlan, 
    config: ProjectConfig, 
    ctx: Context
) -> None:
    """Generate server code and configuration
    
    Args:
        project_path: Path to project
        plan: Generation plan
        config: Project configuration
        ctx: FastMCP context
    """
    await ctx.info(LOG_MESSAGES["generating_code"])
    
    generate_server_code(
        project_path,
        plan,
        config.python_version,
        config.additional_dependencies
    )
    
    await ctx.info(LOG_MESSAGES["server_generated"])


async def generate_docs(
    project_path: Path,
    plan: GenerationPlan,
    config: ProjectConfig,
    ctx: Context
) -> None:
    """Generate documentation files
    
    Args:
        project_path: Path to project
        plan: Generation plan
        config: Project configuration
        ctx: FastMCP context
    """
    await ctx.info(LOG_MESSAGES["generating_docs"])
    
    generate_documentation(
        project_path,
        plan,
        config.project_name,
        config.python_version
    )
    
    await ctx.info(LOG_MESSAGES["docs_generated"])


async def generate_tests(
    project_path: Path,
    plan: GenerationPlan,
    config: ProjectConfig,
    ctx: Context
) -> None:
    """Generate test suite
    
    Args:
        project_path: Path to project
        plan: Generation plan
        config: Project configuration
        ctx: FastMCP context
    """
    await ctx.info(LOG_MESSAGES["generating_tests"])
    
    generate_test_file(
        project_path,
        plan,
        config.project_name
    )
    
    await ctx.info(LOG_MESSAGES["tests_generated"])


async def generate_tests_to_scripts(
    scripts_path: Path,
    project_path: Path,
    plan: GenerationPlan,
    config: ProjectConfig,
    ctx: Context
) -> None:
    """Generate test suite in scripts directory with correct import paths
    
    Args:
        scripts_path: Path to scripts directory
        project_path: Path to MCP project directory
        plan: Generation plan
        config: Project configuration
        ctx: FastMCP context
    """
    await ctx.info("Generating test suite in scripts directory...")
    
    from ken_mcp.generators.tests import generate_test_file_to_scripts
    generate_test_file_to_scripts(
        scripts_path,
        project_path,
        plan,
        config.project_name
    )
    
    await ctx.info("Test suite generated in scripts/")


def create_diagnostic_script_to_scripts(
    scripts_path: Path,
    project_path: Path, 
    project_name: str,
    python_version: str = "3.10"
) -> None:
    """Create diagnostic script in scripts directory with correct import paths
    
    Args:
        scripts_path: Path to scripts directory
        project_path: Path to MCP project directory
        project_name: Project name
        python_version: Python version
    """
    from ken_mcp.generators.project import create_diagnostic_script_to_scripts as create_diag
    create_diag(scripts_path, project_path, project_name, python_version)


async def generate_help_docs(
    root_path: Path,
    project_path: Path,
    plan: GenerationPlan,
    config: ProjectConfig,
    ctx: Context
) -> None:
    """Generate help.md in root directory
    
    Args:
        root_path: Path to root directory
        project_path: Path to MCP project directory  
        plan: Generation plan
        config: Project configuration
        ctx: FastMCP context
    """
    await ctx.info("Generating help documentation in root directory...")
    
    from ken_mcp.generators.docs import generate_help_to_root
    generate_help_to_root(
        root_path,
        project_path,
        plan,
        config.project_name,
        config.python_version
    )
    
    await ctx.info("Help documentation generated in root/")


async def generate_readme_docs(
    root_path: Path,
    plan: GenerationPlan,
    config: ProjectConfig,
    ctx: Context
) -> None:
    """Generate README.md in root directory
    
    Args:
        root_path: Path to root directory
        plan: Generation plan
        config: Project configuration
        ctx: FastMCP context
    """
    await ctx.info("Generating README.md in root directory...")
    
    from ken_mcp.generators.docs import generate_readme_to_root
    generate_readme_to_root(
        root_path,
        config.project_name,
        plan.description
    )
    
    await ctx.info("README.md generated in root/")


async def validate_generated_project(project_path: Path, ctx: Context) -> dict:
    """Validate the generated project
    
    Args:
        project_path: Path to project
        ctx: FastMCP context
        
    Returns:
        Validation results
    """
    await ctx.info(LOG_MESSAGES["validating_project"])
    
    validation = validate_project(project_path)
    
    if not validation["valid"]:
        await ctx.info(f"⚠️ Validation issues: {', '.join(validation['issues'])}")
    
    return validation


def generate_next_steps(project_path: Path) -> List[str]:
    """Generate platform-specific list of next steps for user
    
    Args:
        project_path: Path to generated project
        
    Returns:
        List of next step instructions tailored to user's platform
    """
    from ..utils.platform import detect_platform
    
    # Detect user's platform for tailored instructions
    platform_info = detect_platform()
    python_cmd = platform_info.best_python or "python3"
    
    steps = [
        f"1. cd {project_path}",
        f"2. {platform_info.get_install_command()}",
        f"3. cd .. && {python_cmd} scripts/test.py  # Run tests to verify the MCP works",
        f"4. Fix any failing tests in {project_path.name}/server.py",
        f"5. {python_cmd} scripts/verify.py  # Check for placeholders and TODOs",
        f"6. Fix all implementation issues identified by verify.py",
    ]
    
    # Add platform-specific claude mcp add command with global scope recommendation
    if platform_info.is_windows:
        steps.append(f"7. Add to Claude (Global - Recommended): claude mcp add <name> -s user \"{python_cmd} {project_path}\\\\run_server.py\"")
        steps.append(f"   Alternative (Local): claude mcp add <name> \"{python_cmd} {project_path}\\\\run_server.py\"")
        steps.append("   Alternative (Batch): claude mcp add <name> -s user \"{project_path}\\\\run_server.bat\"")
    else:
        steps.append(f"7. Add to Claude (Global - Recommended): claude mcp add <name> -s user \"{project_path}/run_server.py\"")
        steps.append(f"   Alternative (Local): claude mcp add <name> \"{project_path}/run_server.py\"")
        steps.append(f"   Alternative (With Python): claude mcp add <name> -s user \"{python_cmd} {project_path}/run_server.py\"")
    
    steps.extend([
        "   💡 Global (-s user) = Works from any directory",
        "   💡 Local (no flag) = Only works from current directory", 
        "8. claude mcp list  # Confirm MCP was added to config",
        "9. Exit and restart Claude Code for MCP to become active",
        "10. claude mcp list  # Verify MCP shows as Active ✓ (not Failed ✗)",
        "11. Verify connection with: /mcp (should show connected ✔)",
        "",
        "💡 TIP: Run 'python3 scripts/diagnose.py' for platform-specific troubleshooting!"
    ])
    
    return steps