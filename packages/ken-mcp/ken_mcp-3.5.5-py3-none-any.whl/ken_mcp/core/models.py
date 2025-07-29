"""
Data models for KEN-MCP generator
Defines configuration and result classes for type safety
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ParameterDefinition:
    """Definition for a tool/prompt parameter"""
    name: str
    type: str
    description: str
    default: Optional[Any] = None
    required: bool = True


@dataclass
class ToolDefinition:
    """Definition for an MCP tool"""
    name: str
    description: str
    parameters: List[ParameterDefinition] = field(default_factory=list)
    implementation: str = "boilerplate"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "default": p.default
                } for p in self.parameters
            ],
            "implementation": self.implementation
        }


@dataclass
class ResourceDefinition:
    """Definition for an MCP resource"""
    uri_pattern: str
    description: str
    implementation: str = "boilerplate"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility"""
        return {
            "uri_pattern": self.uri_pattern,
            "description": self.description,
            "implementation": self.implementation
        }


@dataclass
class PromptDefinition:
    """Definition for an MCP prompt"""
    name: str
    description: str
    parameters: List[ParameterDefinition] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "default": p.default
                } for p in self.parameters
            ]
        }


@dataclass
class GenerationPlan:
    """Plan for generating an MCP server"""
    description: str
    tools: List[ToolDefinition] = field(default_factory=list)
    resources: List[ResourceDefinition] = field(default_factory=list)
    prompts: List[PromptDefinition] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    original_requirements: str = ""
    analysis_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility"""
        return {
            "description": self.description,
            "tools": [t.to_dict() for t in self.tools],
            "resources": [r.to_dict() for r in self.resources],
            "prompts": [p.to_dict() for p in self.prompts],
            "dependencies": self.dependencies,
            "original_requirements": self.original_requirements
        }


@dataclass
class ProjectConfig:
    """Configuration for MCP project generation"""
    requirements: str
    project_name: str
    output_dir: Optional[str] = None
    include_resources: bool = True
    include_prompts: bool = True
    python_version: str = "3.10"
    additional_dependencies: Optional[List[str]] = None
    
    def validate(self) -> List[str]:
        """Validate configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.requirements:
            errors.append("Requirements cannot be empty")
        
        if not self.project_name:
            errors.append("Project name cannot be empty")
        elif len(self.project_name) > 50:
            errors.append("Project name too long (max 50 characters)")
        
        # Validate Python version format
        import re
        if not re.match(r'^\d+\.\d+$', self.python_version):
            errors.append("Python version must be in format X.Y (e.g., 3.10)")
        
        return errors


@dataclass
class GenerationResult:
    """Result of MCP server generation"""
    success: bool
    project_path: Path
    project_name: str
    tools_generated: int = 0
    resources_generated: int = 0
    prompts_generated: int = 0
    validation: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "success": self.success,
            "project_path": str(self.project_path),
            "project_name": self.project_name,
            "tools_generated": self.tools_generated,
            "resources_generated": self.resources_generated,
            "prompts_generated": self.prompts_generated,
            "validation": self.validation,
            "next_steps": self.next_steps,
            "error": self.error
        }


@dataclass
class ValidationResult:
    """Result of project validation"""
    valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    files_checked: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "files_checked": self.files_checked
        }


@dataclass
class TestCase:
    """Definition of a test case"""
    name: str
    description: str
    test_type: str  # "valid", "missing_param", "invalid_type", "edge_case"
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_behavior: str = ""