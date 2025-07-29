"""
Requirements analyzer for KEN-MCP
Analyzes requirements and creates generation plans with intelligent tool structures
"""

from typing import List, Dict, Any
from ken_mcp.core.models import (
    GenerationPlan, ToolDefinition, ResourceDefinition, 
    PromptDefinition, ParameterDefinition
)
from ken_mcp.core.requirement_parser import RequirementParser
from ken_mcp.utils.text import clean_requirements
from ken_mcp.utils.suggestions import suggest_dependencies


def analyze_and_plan(
    requirements: str, 
    include_resources: bool = True, 
    include_prompts: bool = True
) -> GenerationPlan:
    """Create a generation plan based on intelligent requirement analysis
    
    Args:
        requirements: Natural language requirements
        include_resources: Whether to include resources
        include_prompts: Whether to include prompts
        
    Returns:
        Generation plan with intelligently structured tools, resources, and prompts
    """
    # Parse requirements to extract meaningful components
    parser = RequirementParser()
    parsed = parser.parse(requirements)
    
    # Clean requirements for description
    clean_reqs = clean_requirements(requirements, max_length=100)
    
    # Create base plan with rich context
    plan = GenerationPlan(
        description=f"MCP server for: {clean_reqs}",
        original_requirements=requirements
    )
    
    # Add analysis results as context for Claude
    plan.analysis_context = {
        "domain": parsed.domain,
        "primary_actions": parsed.primary_actions,
        "entities": parsed.entities,
        "operations": parsed.operations,
        "attributes": parsed.attributes,
        "technical_terms": parsed.technical_terms
    }
    
    # Generate tools based on parsed requirements
    plan.tools = generate_intelligent_tools(parsed, requirements)
    
    # Generate resources if requested - always generate at least one
    if include_resources:
        plan.resources = generate_intelligent_resources(parsed, requirements)
        # Ensure at least one resource exists
        if not plan.resources:
            plan.resources = [ResourceDefinition(
                uri_pattern="data://items",
                description=f"Default resource collection for {parsed.domain} operations - TODO: Customize based on requirements",
                implementation="intelligent"
            )]
    
    # Generate prompts if requested
    if include_prompts:
        plan.prompts = generate_intelligent_prompts(parsed, requirements)
    
    # Add dependencies based on analysis - include service-specific ones
    plan.dependencies = suggest_enhanced_dependencies(requirements, parsed)
    
    return plan


def generate_intelligent_tools(parsed, requirements: str) -> List[ToolDefinition]:
    """Generate intelligently structured tools based on parsed requirements
    
    Args:
        parsed: Parsed requirement data
        requirements: Original requirements text
        
    Returns:
        List of tool definitions with meaningful names and structures
    """
    tools = []
    
    # Use suggested tools from parser
    for i, suggestion in enumerate(parsed.suggested_tools):
        tool_name = suggestion['name']
        tool_type = suggestion['type']
        entity = suggestion.get('entity', 'data')
        likely_params = suggestion.get('likely_params', ['input'])
        
        # Build parameter list based on tool type
        parameters = []
        
        if tool_type == 'create':
            parameters.extend([
                ParameterDefinition(
                    name=entity + "_data",
                    type="Dict[str, Any]",
                    description=f"Data for creating {entity}"
                ),
                ParameterDefinition(
                    name="validate",
                    type="bool",
                    description="Whether to validate before creating",
                    default=True,
                    required=False
                )
            ])
        
        elif tool_type == 'read' or tool_type == 'get':
            parameters.append(
                ParameterDefinition(
                    name=f"{entity}_id",
                    type="str",
                    description=f"ID of the {entity} to retrieve"
                )
            )
        
        elif tool_type == 'list':
            parameters.extend([
                ParameterDefinition(
                    name="limit",
                    type="int",
                    description="Maximum number of items to return",
                    default=100,
                    required=False
                ),
                ParameterDefinition(
                    name="offset",
                    type="int",
                    description="Number of items to skip",
                    default=0,
                    required=False
                ),
                ParameterDefinition(
                    name="filter",
                    type="Optional[Dict[str, Any]]",
                    description="Filter criteria",
                    default=None,
                    required=False
                )
            ])
        
        elif tool_type == 'update':
            parameters.extend([
                ParameterDefinition(
                    name=f"{entity}_id",
                    type="str",
                    description=f"ID of the {entity} to update"
                ),
                ParameterDefinition(
                    name="updates",
                    type="Dict[str, Any]",
                    description="Fields to update"
                ),
                ParameterDefinition(
                    name="partial",
                    type="bool",
                    description="Whether to allow partial updates",
                    default=True,
                    required=False
                )
            ])
        
        elif tool_type == 'delete':
            parameters.extend([
                ParameterDefinition(
                    name=f"{entity}_id",
                    type="str",
                    description=f"ID of the {entity} to delete"
                ),
                ParameterDefinition(
                    name="confirm",
                    type="bool",
                    description="Confirmation to prevent accidental deletion",
                    default=False
                )
            ])
        
        elif tool_type == 'process':
            parameters.extend([
                ParameterDefinition(
                    name="input_data",
                    type="Any",
                    description="Data to process"
                ),
                ParameterDefinition(
                    name="options",
                    type="Optional[Dict[str, Any]]",
                    description="Processing options",
                    default=None,
                    required=False
                )
            ])
        
        elif tool_type == 'monitor':
            parameters.extend([
                ParameterDefinition(
                    name="target",
                    type="str",
                    description="What to monitor"
                ),
                ParameterDefinition(
                    name="interval",
                    type="int",
                    description="Check interval in seconds",
                    default=60,
                    required=False
                ),
                ParameterDefinition(
                    name="threshold",
                    type="Optional[Dict[str, float]]",
                    description="Alert thresholds",
                    default=None,
                    required=False
                )
            ])
        
        else:
            # Generic parameters based on likely params
            for param in likely_params[:3]:  # Max 3 params to stay under limit
                param_type = "str" if param in ['name', 'id', 'type'] else "Any"
                parameters.append(
                    ParameterDefinition(
                        name=param,
                        type=param_type,
                        description=f"{param.replace('_', ' ').title()} parameter"
                    )
                )
        
        # Create rich description with context
        description = f"""
{tool_type.title()} operation for {entity}.

Domain: {parsed.domain}
Related operations: {', '.join(parsed.operations[:3]) if parsed.operations else 'general'}

TODO: Claude, implement this tool based on the requirements:
{requirements}

Consider:
- What specific {entity} operations are needed
- What validation should be performed
- What error cases to handle
- What response format makes sense
"""
        
        tools.append(ToolDefinition(
            name=tool_name,
            description=description.strip(),
            parameters=parameters[:4],  # Respect max 4 params limit
            implementation="intelligent"
        ))
    
    # If no tools were generated, create at least one meaningful tool
    if not tools:
        tools.append(ToolDefinition(
            name="process_request",
            description=f"""
Main processing tool for this MCP.

TODO: Claude, implement based on requirements:
{requirements}

Detected domain: {parsed.domain}
Detected actions: {', '.join(parsed.primary_actions)}
""",
            parameters=[
                ParameterDefinition(
                    name="request_data",
                    type="Dict[str, Any]",
                    description="Request data to process"
                ),
                ParameterDefinition(
                    name="options",
                    type="Optional[Dict[str, Any]]",
                    description="Processing options",
                    default=None,
                    required=False
                )
            ],
            implementation="intelligent"
        ))
    
    # Ensure minimum 3 tools
    while len(tools) < 3:
        # Add generic tools based on domain
        if len(tools) == 1:
            tools.append(ToolDefinition(
                name="list_all",
                description=f"List all items in the {parsed.domain} system\n\nTODO: Claude, implement based on requirements",
                parameters=[
                    ParameterDefinition(
                        name="filter",
                        type="Optional[Dict[str, Any]]",
                        description="Optional filter criteria",
                        default=None,
                        required=False
                    )
                ],
                implementation="intelligent"
            ))
        elif len(tools) == 2:
            tools.append(ToolDefinition(
                name="get_status",
                description=f"Get status information for {parsed.domain}\n\nTODO: Claude, implement based on requirements",
                parameters=[
                    ParameterDefinition(
                        name="detailed",
                        type="bool",
                        description="Whether to include detailed information",
                        default=False,
                        required=False
                    )
                ],
                implementation="intelligent"
            ))
    
    return tools


def generate_intelligent_resources(parsed, requirements: str) -> List[ResourceDefinition]:
    """Generate resources based on parsed requirements
    
    Args:
        parsed: Parsed requirement data
        requirements: Original requirements text
        
    Returns:
        List of resource definitions
    """
    resources = []
    
    # Always generate entity-based resources if we have entities
    if parsed.entities:
        # Generate resources for primary entity
        primary_entity = parsed.entities[0]
        # Clean entity name for URI (replace spaces with underscores)
        uri_entity = primary_entity.replace(" ", "_")
        
        resources.append(ResourceDefinition(
            uri_pattern=f"data://{uri_entity}s",
            description=f"Collection of {primary_entity}s - TODO: Implement based on requirements",
            implementation="intelligent"
        ))
        resources.append(ResourceDefinition(
            uri_pattern=f"data://{uri_entity}/{{id}}",
            description=f"Individual {primary_entity} by ID - TODO: Implement based on requirements",
            implementation="intelligent"
        ))
        
        # Add a second entity resource if available
        if len(parsed.entities) > 1:
            second_entity = parsed.entities[1].replace(" ", "_")
            resources.append(ResourceDefinition(
                uri_pattern=f"data://{second_entity}s",
                description=f"Collection of {parsed.entities[1]}s - TODO: Implement based on requirements",
                implementation="intelligent"
            ))
    
    # Add domain-specific resources
    domain_resources = {
        'api_integration': [
            ("api://endpoints", "Available API endpoints and their configurations"),
            ("api://status", "Current API connection status and health")
        ],
        'database': [
            ("db://schema", "Database schema information"),
            ("db://connections", "Active database connections")
        ],
        'communication': [
            ("channels://list", "Available communication channels"),
            ("users://active", "Active users in the system")
        ],
        'file_system': [
            ("files://recent", "Recently accessed files"),
            ("dirs://structure", "Directory structure information")
        ],
        'web_tools': [
            ("web://scraped", "Scraped web content"),
            ("web://cache", "Cached web resources")
        ],
        'cloud_services': [
            ("cloud://resources", "Cloud resource inventory"),
            ("cloud://costs", "Cloud cost information")
        ],
        'development_tools': [
            ("repos://list", "Available repositories"),
            ("builds://recent", "Recent build information")
        ],
        'productivity': [
            ("workspace://projects", "Active projects"),
            ("workspace://tasks", "Current tasks and assignments")
        ]
    }
    
    if parsed.domain in domain_resources:
        for uri, desc in domain_resources[parsed.domain]:
            resources.append(ResourceDefinition(
                uri_pattern=uri,
                description=f"{desc} - TODO: Implement based on requirements",
                implementation="intelligent"
            ))
    
    # Add config resource if authentication or configuration detected
    if any(term in requirements.lower() for term in ['config', 'settings', 'auth', 'api key', 'credential']):
        resources.append(ResourceDefinition(
            uri_pattern="config://settings",
            description="Configuration and settings - TODO: Implement based on requirements",
            implementation="intelligent"
        ))
    
    # Add status resource for monitoring/health checks
    if not any(r.uri_pattern.endswith('status') for r in resources):
        resources.append(ResourceDefinition(
            uri_pattern="system://status",
            description=f"System status for {parsed.domain} - TODO: Implement health checks",
            implementation="intelligent"
        ))
    
    return resources


def generate_intelligent_prompts(parsed, requirements: str) -> List[PromptDefinition]:
    """Generate prompts based on parsed requirements
    
    Args:
        parsed: Parsed requirement data
        requirements: Original requirements text
        
    Returns:
        List of prompt definitions
    """
    prompts = []
    
    # Always include a help prompt tailored to the domain
    prompts.append(PromptDefinition(
        name="help",
        description=f"Get help with {parsed.domain} operations - TODO: Customize for this MCP",
        parameters=[
            ParameterDefinition(
                name="topic",
                type="Optional[str]",
                description="Specific topic to get help about",
                default=None,
                required=False
            )
        ]
    ))
    
    # Add domain-specific prompts
    if parsed.domain in ['data_science', 'finance', 'monitoring']:
        prompts.append(PromptDefinition(
            name="analyze",
            description=f"Analyze {parsed.domain} data - TODO: Implement analysis logic",
            parameters=[
                ParameterDefinition(
                    name="query",
                    type="str",
                    description="Analysis query"
                ),
                ParameterDefinition(
                    name="context",
                    type="Optional[Dict[str, Any]]",
                    description="Additional context for analysis",
                    default=None,
                    required=False
                )
            ]
        ))
    
    # Add assistant prompt if complex operations detected
    if len(parsed.operations) > 2 or len(parsed.entities) > 2:
        prompts.append(PromptDefinition(
            name="assistant",
            description=f"AI assistant for {parsed.domain} tasks - TODO: Implement based on requirements",
            parameters=[
                ParameterDefinition(
                    name="request",
                    type="str",
                    description="Natural language request"
                )
            ]
        ))
    
    return prompts


def suggest_enhanced_dependencies(requirements: str, parsed) -> List[str]:
    """Suggest dependencies including service-specific ones
    
    Args:
        requirements: Original requirements text
        parsed: Parsed requirement data
        
    Returns:
        List of dependencies including service-specific packages
    """
    # Start with basic dependencies from suggestions
    deps = set(suggest_dependencies(requirements))
    
    # Add service-specific dependencies based on parsed entities and domain
    req_lower = requirements.lower()
    
    # Database drivers
    if any(term in req_lower for term in ['postgresql', 'postgres']):
        deps.add('psycopg2-binary')
    if any(term in req_lower for term in ['mysql', 'mariadb']):
        deps.add('pymysql')
    if any(term in req_lower for term in ['mongodb', 'mongo']):
        deps.add('pymongo')
    if any(term in req_lower for term in ['redis']):
        deps.update(['redis', 'aioredis'])
    if any(term in req_lower for term in ['elasticsearch', 'elastic']):
        deps.add('elasticsearch')
    if any(term in req_lower for term in ['neo4j']):
        deps.add('neo4j')
    if any(term in req_lower for term in ['influxdb']):
        deps.add('influxdb-client')
    if any(term in req_lower for term in ['cassandra']):
        deps.add('cassandra-driver')
    
    # API/Service SDKs
    if any(term in req_lower for term in ['stripe']):
        deps.add('stripe')
    if any(term in req_lower for term in ['twilio']):
        deps.add('twilio')
    if any(term in req_lower for term in ['sendgrid']):
        deps.add('sendgrid')
    if any(term in req_lower for term in ['aws', 's3', 'ec2', 'lambda']):
        deps.add('boto3')
    if any(term in req_lower for term in ['gcp', 'google cloud']):
        deps.add('google-cloud-storage')
    if any(term in req_lower for term in ['azure']):
        deps.add('azure-storage-blob')
    if any(term in req_lower for term in ['openai', 'gpt']):
        deps.add('openai')
    if any(term in req_lower for term in ['anthropic', 'claude']):
        deps.add('anthropic')
    
    # Communication platforms
    if any(term in req_lower for term in ['slack']):
        deps.add('slack-sdk')
    if any(term in req_lower for term in ['discord']):
        deps.add('discord.py')
    if any(term in req_lower for term in ['telegram']):
        deps.add('python-telegram-bot')
    if any(term in req_lower for term in ['teams', 'microsoft teams']):
        deps.add('botbuilder-core')
    
    # DevOps tools
    if any(term in req_lower for term in ['docker']):
        deps.add('docker')
    if any(term in req_lower for term in ['kubernetes', 'k8s']):
        deps.add('kubernetes')
    if any(term in req_lower for term in ['jenkins']):
        deps.add('python-jenkins')
    if any(term in req_lower for term in ['gitlab']):
        deps.add('python-gitlab')
    if any(term in req_lower for term in ['github']):
        deps.add('PyGithub')
    
    # Monitoring/Observability
    if any(term in req_lower for term in ['prometheus']):
        deps.add('prometheus-client')
    if any(term in req_lower for term in ['datadog']):
        deps.add('datadog')
    if any(term in req_lower for term in ['grafana']):
        deps.add('grafana-api')
    
    # Payment processing
    if any(term in req_lower for term in ['paypal']):
        deps.add('paypalrestsdk')
    if any(term in req_lower for term in ['square']):
        deps.add('squareup')
    
    # Productivity tools
    if any(term in req_lower for term in ['notion']):
        deps.add('notion-client')
    if any(term in req_lower for term in ['linear']):
        deps.add('linear-api')
    if any(term in req_lower for term in ['jira']):
        deps.add('jira')
    if any(term in req_lower for term in ['confluence']):
        deps.add('atlassian-python-api')
    
    # Additional common dependencies based on operations
    if 'webhook' in req_lower:
        deps.add('httpx')
    if any(term in req_lower for term in ['jwt', 'token']):
        deps.add('pyjwt')
    if 'oauth' in req_lower:
        deps.add('authlib')
    
    return sorted(list(deps))