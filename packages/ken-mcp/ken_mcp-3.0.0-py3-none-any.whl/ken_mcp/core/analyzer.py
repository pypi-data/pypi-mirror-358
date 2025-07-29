"""
Requirements analyzer for KEN-MCP
Analyzes requirements and creates generation plans
"""

from typing import List
from ken_mcp.core.models import (
    GenerationPlan, ToolDefinition, ResourceDefinition, 
    PromptDefinition, ParameterDefinition
)
from ken_mcp.utils.text import clean_requirements
from ken_mcp.utils.suggestions import (
    suggest_tool_names,
    suggest_resource_uris, suggest_prompt_names
)


def analyze_and_plan(
    requirements: str, 
    include_resources: bool = True, 
    include_prompts: bool = True
) -> GenerationPlan:
    """Create a generation plan based on requirements
    
    Args:
        requirements: Natural language requirements
        include_resources: Whether to include resources
        include_prompts: Whether to include prompts
        
    Returns:
        Generation plan with tools, resources, and prompts
    """
    # Clean and prepare requirements
    clean_reqs = clean_requirements(requirements, max_length=100)
    
    # Extract key concepts for context (for future use)
    # concepts = extract_key_concepts(requirements)
    
    # Create base plan
    plan = GenerationPlan(
        description=f"MCP server for: {clean_reqs}",
        original_requirements=requirements
    )
    
    # Generate tools
    plan.tools = generate_placeholder_tools(requirements)
    
    # Generate resources if requested
    if include_resources:
        plan.resources = generate_placeholder_resources(requirements)
    
    # Generate prompts if requested
    if include_prompts:
        plan.prompts = generate_placeholder_prompts(requirements)
    
    # Add initial dependencies
    plan.dependencies = ["pathlib", "json", "typing"]
    
    return plan


def generate_placeholder_tools(requirements: str) -> List[ToolDefinition]:
    """Generate placeholder tools based on requirements
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of tool definitions
    """
    tools = []
    
    # Tool 1 - Primary operation
    tool_names = suggest_tool_names(requirements, 0)
    tools.append(ToolDefinition(
        name=tool_names[0] if tool_names else "tool_one",
        description=f"Primary tool - TODO: Implement based on requirements: {requirements}",
        parameters=[
            ParameterDefinition(
                name="input_data",
                type="str",
                description="Main input parameter"
            ),
            ParameterDefinition(
                name="options",
                type="Optional[Dict[str, Any]]",
                description="Additional options",
                default=None,
                required=False
            )
        ],
        implementation="boilerplate"
    ))
    
    # Tool 2 - Secondary operation
    tool_names = suggest_tool_names(requirements, 1)
    tools.append(ToolDefinition(
        name=tool_names[0] if tool_names else "tool_two",
        description=f"Secondary tool - TODO: Implement based on requirements: {requirements}",
        parameters=[
            ParameterDefinition(
                name="param1",
                type="str",
                description="First parameter"
            ),
            ParameterDefinition(
                name="param2",
                type="Optional[int]",
                description="Optional second parameter",
                default=None,
                required=False
            )
        ],
        implementation="boilerplate"
    ))
    
    # Tool 3 - Additional operation
    tool_names = suggest_tool_names(requirements, 2)
    tools.append(ToolDefinition(
        name=tool_names[0] if tool_names else "tool_three",
        description=f"Additional tool - TODO: Implement or remove based on requirements: {requirements}",
        parameters=[
            ParameterDefinition(
                name="data",
                type="Any",
                description="Input data"
            )
        ],
        implementation="boilerplate"
    ))
    
    return tools


def generate_placeholder_resources(requirements: str) -> List[ResourceDefinition]:
    """Generate placeholder resources based on requirements
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of resource definitions
    """
    resources = []
    
    # Get suggested resources
    suggested = suggest_resource_uris(requirements)
    
    if suggested:
        # Use suggestions
        for suggestion in suggested[:3]:  # Limit to 3
            resources.append(ResourceDefinition(
                uri_pattern=suggestion["uri_pattern"],
                description=f"{suggestion['description']} - TODO: Implement based on requirements",
                implementation="boilerplate"
            ))
    else:
        # Default resources
        resources.extend([
            ResourceDefinition(
                uri_pattern="data://items",
                description="TODO: List of items - implement based on requirements",
                implementation="boilerplate"
            ),
            ResourceDefinition(
                uri_pattern="resource://config",
                description="TODO: Configuration data - implement based on requirements",
                implementation="boilerplate"
            ),
            ResourceDefinition(
                uri_pattern="data://status",
                description="TODO: Status information - implement or remove based on requirements",
                implementation="boilerplate"
            )
        ])
    
    return resources


def generate_placeholder_prompts(requirements: str) -> List[PromptDefinition]:
    """Generate placeholder prompts based on requirements
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of prompt definitions
    """
    prompts = []
    
    # Get suggested prompts
    suggested = suggest_prompt_names(requirements)
    
    if suggested:
        # Use suggestions
        for suggestion in suggested[:2]:  # Limit to 2
            if suggestion["name"] == "help":
                prompts.append(PromptDefinition(
                    name="help",
                    description="TODO: Generate contextual help based on requirements",
                    parameters=[
                        ParameterDefinition(
                            name="topic",
                            type="Optional[str]",
                            description="Help topic to get information about",
                            default=None,
                            required=False
                        )
                    ]
                ))
            else:
                prompts.append(PromptDefinition(
                    name=suggestion["name"],
                    description=f"{suggestion['description']} - TODO: Customize based on requirements",
                    parameters=[
                        ParameterDefinition(
                            name="query",
                            type="str",
                            description="User query"
                        )
                    ]
                ))
    else:
        # Default prompts
        prompts.extend([
            PromptDefinition(
                name="help",
                description="TODO: Generate contextual help based on requirements",
                parameters=[
                    ParameterDefinition(
                        name="topic",
                        type="Optional[str]",
                        description="Help topic to get information about",
                        default=None,
                        required=False
                    )
                ]
            ),
            PromptDefinition(
                name="assistant",
                description="TODO: Assistant prompt - customize based on requirements",
                parameters=[
                    ParameterDefinition(
                        name="query",
                        type="str",
                        description="User query",
                        required=True
                    )
                ]
            )
        ])
    
    return prompts