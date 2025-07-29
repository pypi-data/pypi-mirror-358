"""
KEN-MCP: Universal MCP Server Generator

Generates MCP servers for ANY purpose based on natural language requirements.
"""

__version__ = "3.5.2"
__author__ = "KEN-MCP"
__description__ = "AI-powered MCP server generator"

# Delay imports to allow error handling
_mcp = None
_models_imported = False

def _ensure_imports():
    """Ensure imports are loaded"""
    global _mcp, _models_imported
    if not _models_imported:
        from .generator import mcp as _mcp_import
        _mcp = _mcp_import
        _models_imported = True
    return _mcp

# Lazy loading for better error handling
def __getattr__(name):
    """Lazy import attributes"""
    if name == "mcp":
        return _ensure_imports()
    
    # Import models on demand
    if name in ["ProjectConfig", "GenerationPlan", "GenerationResult", 
                "ToolDefinition", "ResourceDefinition", "PromptDefinition",
                "ParameterDefinition", "ValidationResult"]:
        from .core import models
        return getattr(models, name)
    
    if name == "generate_server":
        from .core.orchestrator import generate_mcp_server
        return generate_mcp_server
    
    if name == "analyze_and_plan":
        from .core.analyzer import analyze_and_plan
        return analyze_and_plan
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "mcp",
    "ProjectConfig",
    "GenerationPlan", 
    "GenerationResult",
    "ToolDefinition",
    "ResourceDefinition",
    "PromptDefinition",
    "ParameterDefinition",
    "ValidationResult",
    "generate_server",
    "analyze_and_plan"
]