"""
Project structure generator for KEN-MCP
Handles creation of project directories and basic files
"""

from pathlib import Path
from typing import Optional
from ken_mcp.templates.constants import GITIGNORE_TEMPLATE, ENV_EXAMPLE_TEMPLATE
from ken_mcp.templates.diagnostics import get_diagnostic_script
from ken_mcp.utils.text import sanitize_project_name


def create_project_structure(project_name: str, output_dir: Optional[str] = None) -> Path:
    """Create project directory and basic files
    
    Args:
        project_name: Name of the project
        output_dir: Directory to create project in (optional)
        
    Returns:
        Path to created project directory
    """
    # Sanitize project name for filesystem safety
    safe_name = sanitize_project_name(project_name)
    
    # Determine output directory
    if output_dir:
        base_path = Path(output_dir) / safe_name
    else:
        # Use current working directory
        base_path = Path.cwd() / safe_name
    
    # Create main directory
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Create basic files
    create_gitignore(base_path)
    create_env_example(base_path)
    create_init_file(base_path)
    
    return base_path


def create_gitignore(project_path: Path) -> None:
    """Create .gitignore file
    
    Args:
        project_path: Path to project directory
    """
    (project_path / ".gitignore").write_text(GITIGNORE_TEMPLATE)


def create_env_example(project_path: Path) -> None:
    """Create .env.example file
    
    Args:
        project_path: Path to project directory
    """
    (project_path / ".env.example").write_text(ENV_EXAMPLE_TEMPLATE)


def create_init_file(project_path: Path) -> None:
    """Create __init__.py file
    
    Args:
        project_path: Path to project directory
    """
    (project_path / "__init__.py").write_text('"""Generated MCP server package"""')


def ensure_directory_exists(directory: Path) -> None:
    """Ensure a directory exists, creating if necessary
    
    Args:
        directory: Path to directory
    """
    directory.mkdir(parents=True, exist_ok=True)


def make_executable(file_path: Path) -> None:
    """Make a file executable
    
    Args:
        file_path: Path to file
    """
    import os
    os.chmod(file_path, 0o755)


def create_diagnostic_script(project_path: Path, project_name: str, python_version: str = "3.10") -> None:
    """Create diagnostic script for the project
    
    Args:
        project_path: Path to project directory
        project_name: Name of the project
        python_version: Python version requirement
    """
    diagnostic_content = get_diagnostic_script(project_name, python_version)
    diagnostic_path = project_path / "diagnose.py"
    diagnostic_path.write_text(diagnostic_content)
    make_executable(diagnostic_path)


def create_wrapper_script(project_path: Path, python_version: str = "3.10") -> None:
    """Create cross-platform wrapper scripts to run the MCP server
    
    Args:
        project_path: Path to project directory
        python_version: Python version requirement (used for compatibility checking)
    """
    from ..utils.platform import detect_platform, get_platform_specific_scripts
    
    # Detect the current platform and best Python command
    platform_info = detect_platform()
    python_cmd = platform_info.best_python or "python3"
    
    # Generate all platform-specific scripts
    scripts = get_platform_specific_scripts(python_cmd)
    
    # Create all script files
    for script_name, content in scripts.items():
        script_path = project_path / script_name
        script_path.write_text(content)
        
        # Make executable on Unix systems
        if not script_name.endswith('.bat'):
            make_executable(script_path)