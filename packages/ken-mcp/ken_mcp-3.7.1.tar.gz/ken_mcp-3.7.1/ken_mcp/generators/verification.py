"""
Verification generation for KEN-MCP
Generates verify.py to check for incomplete implementations
"""

from pathlib import Path
import stat

from ken_mcp.core.models import GenerationPlan


def generate_verification_file(project_path: Path, plan: GenerationPlan, project_name: str) -> None:
    """Generate verify.py to check for incomplete implementations
    
    Args:
        project_path: Path to project directory
        plan: Generation plan (for future enhancement)
        project_name: Name of the project
    """
    from ken_mcp.templates.constants import VERIFICATION_TEMPLATE
    
    verification_content = VERIFICATION_TEMPLATE.format(
        project_name=project_name,
        requirements=plan.original_requirements
    )
    
    verification_file = project_path / "verify.py"
    verification_file.write_text(verification_content)
    
    # Make executable
    verification_file.chmod(verification_file.stat().st_mode | stat.S_IEXEC)


def generate_verification_file_to_scripts(
    scripts_path: Path, 
    project_path: Path, 
    plan: GenerationPlan, 
    project_name: str
) -> None:
    """Generate verify.py in scripts directory with correct paths
    
    Args:
        scripts_path: Path to scripts directory
        project_path: Path to MCP project directory
        plan: Generation plan (for future enhancement)
        project_name: Name of the project
    """
    from ken_mcp.templates.constants import VERIFICATION_TEMPLATE_FOR_SCRIPTS
    
    verification_content = VERIFICATION_TEMPLATE_FOR_SCRIPTS.format(
        project_name=project_name,
        project_dir_name=project_path.name,
        requirements=plan.original_requirements
    )
    
    verification_file = scripts_path / "verify.py"
    verification_file.write_text(verification_content)
    
    # Make executable
    verification_file.chmod(verification_file.stat().st_mode | stat.S_IEXEC)