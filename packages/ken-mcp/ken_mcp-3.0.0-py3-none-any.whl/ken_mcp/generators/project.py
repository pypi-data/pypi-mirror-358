"""
Project structure generator for KEN-MCP
Handles creation of project directories and basic files
"""

from pathlib import Path
from typing import Optional
from ken_mcp.templates.constants import GITIGNORE_TEMPLATE, ENV_EXAMPLE_TEMPLATE
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