"""
Suggestion utilities for KEN-MCP generator
Handles tool name suggestions, dependency detection, and concept extraction
"""

from typing import List, Dict
from ken_mcp.templates.constants import (
    DOMAIN_KEYWORDS, DEPENDENCY_SUGGESTIONS, DEFAULT_TOOL_NAMES
)


def extract_key_concepts(requirements: str) -> List[str]:
    """Extract key concepts from requirements for Claude's reference
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of identified concepts
    """
    concepts = []
    req_lower = requirements.lower()
    
    # Check for domain-specific keywords
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(word in req_lower for word in keywords):
            concepts.append(domain.replace('_', ' '))
    
    # Check for common actions
    action_mappings = {
        "creation operations": ["create", "add", "new", "generate"],
        "search functionality": ["search", "find", "query", "lookup"],
        "update operations": ["update", "edit", "modify", "change"],
        "deletion operations": ["delete", "remove", "clear", "purge"],
        "listing operations": ["list", "show", "display", "enumerate"],
        "analysis operations": ["analyze", "process", "calculate", "compute"]
    }
    
    for concept, keywords in action_mappings.items():
        if any(word in req_lower for word in keywords):
            concepts.append(concept)
    
    return concepts if concepts else ["general purpose"]


def suggest_tool_names(requirements: str, index: int) -> List[str]:
    """Suggest possible tool names based on requirements
    
    Args:
        requirements: Natural language requirements
        index: Tool index (0-based)
        
    Returns:
        List of suggested tool names
    """
    req_lower = requirements.lower()
    suggestions = []
    
    # Find matching domain
    domain = None
    for key in ["recipe", "task", "monitor"]:
        if key in req_lower:
            domain = key
            break
    
    # Get suggestions for the domain and index
    if index in DEFAULT_TOOL_NAMES:
        tool_suggestions = DEFAULT_TOOL_NAMES[index]
        if domain and domain in tool_suggestions:
            suggestions = tool_suggestions[domain]
        else:
            suggestions = tool_suggestions["default"]
    else:
        # For indices beyond predefined ones
        suggestions = [f"tool_{index + 1}", f"operation_{index + 1}"]
    
    return suggestions


def suggest_dependencies(requirements: str) -> List[str]:
    """Suggest potential Python dependencies based on requirements
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of suggested package names
    """
    deps = set()
    req_lower = requirements.lower()
    
    # Check each category of dependencies
    dependency_checks = {
        "api_http": ["api", "http", "rest", "webhook", "endpoint"],
        "web_scraping": ["scrape", "web", "html", "crawl"],
        "data_processing": ["csv", "excel", "data"],
        "database": ["database", "sql", "postgres", "mysql"],
        "pdf": ["pdf"],
        "image": ["image"],
        "markdown": ["markdown"],
        "crypto": ["crypto", "bitcoin", "ethereum", "price"],
        "ml_ai": ["classify", "predict", "analyze", "nlp"],
        "websocket": ["websocket", "real-time", "streaming", "live"],
        "auth": ["oauth", "auth", "login", "token"],
        "data_science": ["numpy", "pandas", "matplotlib", "chart"],
        "machine_learning": ["machine learning", "ml", "prediction", "model"],
        "xml": ["xml"]
    }
    
    # Social media specific checks
    social_media_checks = {
        "discord": ["discord"],
        "slack": ["slack"],
        "github": ["github"]
    }
    
    # Add dependencies based on keyword matches
    for category, keywords in dependency_checks.items():
        if any(word in req_lower for word in keywords):
            if category in DEPENDENCY_SUGGESTIONS:
                deps.update(DEPENDENCY_SUGGESTIONS[category])
    
    # Add social media dependencies
    for category, keywords in social_media_checks.items():
        if any(word in req_lower for word in keywords):
            if category in DEPENDENCY_SUGGESTIONS:
                deps.update(DEPENDENCY_SUGGESTIONS[category])
    
    return sorted(list(deps))


def categorize_requirement(requirements: str) -> Dict[str, bool]:
    """Categorize requirements to help with generation decisions
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        Dictionary of feature flags
    """
    req_lower = requirements.lower()
    
    return {
        "needs_env": any(keyword in req_lower for keyword in 
                        ["api", "key", "token", "auth", "database", "url", "webhook"]),
        "needs_storage": any(keyword in req_lower for keyword in 
                           ["store", "save", "persist", "database", "cache"]),
        "needs_api": any(keyword in req_lower for keyword in 
                       ["api", "http", "rest", "endpoint", "webhook"]),
        "needs_async": any(keyword in req_lower for keyword in 
                         ["async", "concurrent", "parallel", "stream", "real-time"]),
        "needs_auth": any(keyword in req_lower for keyword in 
                        ["auth", "login", "token", "oauth", "permission"]),
        "needs_web": any(keyword in req_lower for keyword in 
                       ["web", "scrape", "html", "browser", "download"])
    }


def suggest_resource_uris(requirements: str) -> List[Dict[str, str]]:
    """Suggest resource URIs based on requirements
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of suggested resource definitions
    """
    req_lower = requirements.lower()
    suggestions = []
    
    # Common resource patterns
    if any(word in req_lower for word in ["list", "collection", "items", "data"]):
        suggestions.append({
            "uri_pattern": "data://items",
            "description": "Collection of items"
        })
    
    if any(word in req_lower for word in ["config", "settings", "preferences"]):
        suggestions.append({
            "uri_pattern": "resource://config",
            "description": "Configuration settings"
        })
    
    if any(word in req_lower for word in ["status", "health", "info"]):
        suggestions.append({
            "uri_pattern": "data://status",
            "description": "Status information"
        })
    
    if any(word in req_lower for word in ["template", "example", "sample"]):
        suggestions.append({
            "uri_pattern": "resource://templates",
            "description": "Templates and examples"
        })
    
    return suggestions


def suggest_prompt_names(requirements: str) -> List[Dict[str, str]]:
    """Suggest prompt names based on requirements
    
    Args:
        requirements: Natural language requirements
        
    Returns:
        List of suggested prompt definitions
    """
    req_lower = requirements.lower()
    suggestions = []
    
    # Always include a help prompt
    suggestions.append({
        "name": "help",
        "description": "Get help with using the MCP server"
    })
    
    # Context-specific prompts
    if any(word in req_lower for word in ["assist", "guide", "help", "support"]):
        suggestions.append({
            "name": "assistant",
            "description": "Interactive assistant for guidance"
        })
    
    if any(word in req_lower for word in ["example", "demo", "sample"]):
        suggestions.append({
            "name": "examples",
            "description": "Show usage examples"
        })
    
    if any(word in req_lower for word in ["analyze", "suggest", "recommend"]):
        suggestions.append({
            "name": "analyze",
            "description": "Analyze data and provide recommendations"
        })
    
    return suggestions