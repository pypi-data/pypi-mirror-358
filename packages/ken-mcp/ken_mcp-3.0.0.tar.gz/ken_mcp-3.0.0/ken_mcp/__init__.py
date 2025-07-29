"""
KEN-MCP: Universal MCP Server Generator

Generates MCP servers for ANY purpose based on natural language requirements.
"""

__version__ = "2.1.8"
__author__ = "KEN-MCP"
__description__ = "AI-powered MCP server generator"

from .generator import mcp

# Core models
from .core.models import (
    ProjectConfig,
    GenerationPlan,
    GenerationResult,
    ToolDefinition,
    ResourceDefinition,
    PromptDefinition,
    ParameterDefinition,
    ValidationResult
)

# Main functions
from .core.orchestrator import generate_mcp_server as generate_server
from .core.analyzer import analyze_and_plan

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