"""
Text processing utilities for KEN-MCP generator
Handles string escaping, cleaning, and truncation
"""

try:
    from ken_mcp.templates.constants import MAX_DOCSTRING_LENGTH
except ImportError:
    # Fallback for testing
    MAX_DOCSTRING_LENGTH = 500


def escape_for_docstring(text: str) -> str:
    """Escape text to be safely used in Python docstrings
    
    Args:
        text: Raw text to escape
        
    Returns:
        Escaped text safe for docstring usage
    """
    # Replace all quotes to avoid issues with docstring delimiters
    text = text.replace('"', "'")
    # Escape backslashes
    text = text.replace("\\", "\\\\")
    # Remove any trailing/leading whitespace that could cause issues
    text = text.strip()
    # Limit length to prevent extremely long docstrings
    if len(text) > MAX_DOCSTRING_LENGTH:
        text = text[:MAX_DOCSTRING_LENGTH - 3] + "..."
    return text


def clean_requirements(requirements: str, max_length: int = 100) -> str:
    """Clean up requirements text for descriptions
    
    Args:
        requirements: Raw requirements text
        max_length: Maximum length for output
        
    Returns:
        Cleaned requirements string
    """
    # Remove newlines and excessive spaces
    clean = ' '.join(requirements.split())
    # Truncate if needed
    if len(clean) > max_length:
        return clean[:max_length] + '...'
    return clean


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to specified length with ellipsis
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_project_name(name: str) -> str:
    """Sanitize project name for filesystem safety
    
    Args:
        name: Raw project name
        
    Returns:
        Sanitized name safe for filesystem
    """
    import re
    # Replace non-alphanumeric characters with underscore
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())


def format_json_string(obj) -> str:
    """Format object as JSON string for embedding in code
    
    Args:
        obj: Object to format
        
    Returns:
        JSON string representation
    """
    import json
    return json.dumps(obj)


def indent_text(text: str, spaces: int = 4) -> str:
    """Indent all lines of text by specified spaces
    
    Args:
        text: Text to indent
        spaces: Number of spaces to indent
        
    Returns:
        Indented text
    """
    indent = ' ' * spaces
    lines = text.split('\n')
    return '\n'.join(indent + line if line else line for line in lines)