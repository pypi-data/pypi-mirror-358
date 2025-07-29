"""
Advanced requirement parser for KEN-MCP
Analyzes natural language requirements to generate meaningful MCP structures
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ParsedRequirement:
    """Parsed requirement with extracted components"""
    domain: str
    primary_actions: List[str]
    entities: List[str]
    operations: List[str]
    attributes: List[str]
    technical_terms: List[str]
    suggested_tools: List[Dict[str, any]]


class RequirementParser:
    """Parse natural language requirements into structured components"""
    
    # Common action verbs that indicate tool operations
    ACTION_VERBS = {
        'create': ['create', 'add', 'new', 'generate', 'make', 'build', 'construct', 'initialize'],
        'read': ['read', 'get', 'fetch', 'retrieve', 'list', 'show', 'display', 'view', 'find', 'search'],
        'update': ['update', 'edit', 'modify', 'change', 'set', 'configure', 'adjust', 'alter'],
        'delete': ['delete', 'remove', 'clear', 'purge', 'destroy', 'clean', 'erase'],
        'process': ['process', 'analyze', 'calculate', 'compute', 'transform', 'convert', 'parse'],
        'monitor': ['monitor', 'watch', 'track', 'observe', 'check', 'detect', 'alert'],
        'connect': ['connect', 'integrate', 'sync', 'link', 'bind', 'interface'],
        'validate': ['validate', 'verify', 'check', 'test', 'ensure', 'confirm'],
        'manage': ['manage', 'control', 'handle', 'organize', 'coordinate'],
        'send': ['send', 'notify', 'email', 'message', 'publish', 'broadcast'],
        'authenticate': ['authenticate', 'auth', 'login', 'authorize', 'verify']
    }
    
    # Domain indicators - aligned with actual MCP use cases
    DOMAIN_PATTERNS = {
        'api_integration': ['api', 'rest', 'graphql', 'webhook', 'endpoint', 'oauth', 'integration', 'service'],
        'database': ['database', 'sql', 'postgres', 'mysql', 'mongodb', 'sqlite', 'query', 'table', 'schema'],
        'file_system': ['file', 'directory', 'folder', 'path', 'storage', 'document', 'read', 'write'],
        'development_tools': ['git', 'github', 'gitlab', 'commit', 'branch', 'pull request', 'ci/cd', 'code', 'repository'],
        'productivity': ['notion', 'linear', 'todoist', 'task', 'project', 'management', 'organize', 'workflow'],
        'communication': ['slack', 'discord', 'email', 'message', 'chat', 'notification', 'channel', 'conversation'],
        'web_tools': ['scrape', 'browser', 'puppeteer', 'selenium', 'crawl', 'fetch', 'search', 'web'],
        'cloud_services': ['aws', 'gcp', 'azure', 'cloud', 's3', 'lambda', 'kubernetes', 'docker'],
        'ai_tools': ['rag', 'vector', 'embedding', 'prompt', 'llm', 'model', 'inference', 'chain'],
        'data_analytics': ['analytics', 'metrics', 'dashboard', 'visualization', 'report', 'bi', 'chart', 'statistics']
    }
    
    def parse(self, requirements: str) -> ParsedRequirement:
        """Parse requirements into structured components
        
        Args:
            requirements: Natural language requirements
            
        Returns:
            Parsed requirement with extracted components
        """
        req_lower = requirements.lower()
        
        # Extract domain
        domain = self._identify_domain(req_lower)
        
        # Extract actions
        primary_actions = self._extract_actions(req_lower)
        
        # Extract entities (nouns that represent things to operate on)
        entities = self._extract_entities(requirements)
        
        # Extract operations (specific things to do)
        operations = self._extract_operations(req_lower)
        
        # Extract attributes (properties or characteristics)
        attributes = self._extract_attributes(requirements)
        
        # Extract technical terms
        technical_terms = self._extract_technical_terms(requirements)
        
        # Generate suggested tools based on analysis
        suggested_tools = self._generate_tool_suggestions(
            domain, primary_actions, entities, operations, requirements
        )
        
        return ParsedRequirement(
            domain=domain,
            primary_actions=primary_actions,
            entities=entities,
            operations=operations,
            attributes=attributes,
            technical_terms=technical_terms,
            suggested_tools=suggested_tools
        )
    
    def _identify_domain(self, req_lower: str) -> str:
        """Identify the primary domain of the requirements"""
        for domain, keywords in self.DOMAIN_PATTERNS.items():
            if any(keyword in req_lower for keyword in keywords):
                return domain
        return 'general'
    
    def _extract_actions(self, req_lower: str) -> List[str]:
        """Extract primary action verbs from requirements"""
        actions = []
        for action_type, verbs in self.ACTION_VERBS.items():
            if any(verb in req_lower for verb in verbs):
                actions.append(action_type)
        return actions if actions else ['process']
    
    def _extract_entities(self, requirements: str) -> List[str]:
        """Extract entities (nouns) that are operated on"""
        req_lower = requirements.lower()
        entities = []
        
        # Extract service names from original case
        service_patterns = [
            r'(?:integrate|interface|connect)\s+(?:with\s+)?([A-Z][a-zA-Z]+)',  # integrate with ServiceName
            r'([A-Z][a-zA-Z]+)\s+(?:api|integration|service)',  # ServiceName API/integration
            r'(?:using|via|through)\s+([A-Z][a-zA-Z]+)',        # using ServiceName
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, requirements)  # Use original case
            entities.extend([m.lower() for m in matches if m])
        
        # Look for specific entity patterns in lowercase
        entity_patterns = [
            # MCP-relevant patterns
            r'(?:fetch|retrieve|get)\s+(\w+)\s+from',           # fetch X from
            r'(?:send|post|publish)\s+(\w+)\s+to',              # send X to
            r'(?:list|create|update|delete)\s+(\w+)',           # CRUD operations
            r'(\w+)\s+(?:api|endpoint|resource)',               # X api/endpoint
            r'(\w+)\s+(?:database|table|collection)',           # X database/table
            r'manage\s+(\w+)\s+(?:in|on)',                      # manage X in/on
            r'(?:query|search)\s+(\w+)',                        # query/search X
            r'(\w+)\s+(?:management|integration|automation)',   # X management/integration
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, req_lower)
            # Flatten tuples from multiple capture groups
            for match in matches:
                if isinstance(match, tuple):
                    entities.extend([m for m in match if m])
                else:
                    entities.append(match)
        
        # Domain-specific entity extraction for MCP use cases - enhanced patterns
        if any(term in req_lower for term in ['github', 'gitlab', 'git', 'repository']):
            # Look for development entities
            dev_entities = re.findall(r'(repository|repo|issue|commit|branch|pr|pull\s*request|workflow|release|tag|fork|merge|code|review)', req_lower)
            entities.extend(dev_entities)
        
        if any(term in req_lower for term in ['slack', 'discord', 'teams', 'email', 'message', 'chat']):
            # Look for communication entities
            comm_entities = re.findall(r'(message|channel|user|thread|conversation|notification|workspace|member|attachment|reaction|dm|direct\s*message)', req_lower)
            entities.extend(comm_entities)
        
        if any(term in req_lower for term in ['database', 'postgres', 'mysql', 'mongodb', 'sqlite', 'sql']):
            # Look for database entities
            db_entities = re.findall(r'(table|query|record|schema|collection|document|index|view|procedure|trigger|constraint|column|row|field)', req_lower)
            entities.extend(db_entities)
        
        if any(term in req_lower for term in ['notion', 'linear', 'jira', 'confluence', 'asana', 'trello']):
            # Look for productivity entities
            prod_entities = re.findall(r'(task|project|page|workspace|board|ticket|issue|epic|sprint|story|subtask|comment|attachment)', req_lower)
            entities.extend(prod_entities)
        
        if any(term in req_lower for term in ['api', 'rest', 'graphql', 'service', 'endpoint']):
            # Look for API entities
            api_entities = re.findall(r'(endpoint|resource|request|response|authentication|header|payload|method|route|parameter|token)', req_lower)
            entities.extend(api_entities)
        
        if any(term in req_lower for term in ['stripe', 'payment', 'billing', 'subscription', 'invoice']):
            # Look for payment entities
            payment_entities = re.findall(r'(payment|customer|subscription|invoice|charge|refund|product|price|plan|card|transaction)', req_lower)
            entities.extend(payment_entities)
        
        if any(term in req_lower for term in ['aws', 'gcp', 'azure', 'cloud', 's3', 'lambda']):
            # Look for cloud entities
            cloud_entities = re.findall(r'(instance|bucket|function|container|cluster|service|resource|region|zone|vpc|subnet)', req_lower)
            entities.extend(cloud_entities)
        
        if any(term in req_lower for term in ['docker', 'kubernetes', 'k8s', 'container', 'deployment']):
            # Look for container entities
            container_entities = re.findall(r'(container|pod|service|deployment|namespace|ingress|configmap|secret|volume|node)', req_lower)
            entities.extend(container_entities)
        
        if any(term in req_lower for term in ['elasticsearch', 'elastic', 'search', 'index']):
            # Look for search entities
            search_entities = re.findall(r'(index|document|mapping|query|aggregation|filter|analyzer|field|shard|cluster)', req_lower)
            entities.extend(search_entities)
        
        if any(term in req_lower for term in ['redis', 'cache', 'memcached', 'key-value']):
            # Look for cache entities
            cache_entities = re.findall(r'(key|value|cache|ttl|expire|hash|list|set|sorted\s*set|pub|sub|channel)', req_lower)
            entities.extend(cache_entities)
        
        # Clean up entities
        entities = [e.rstrip('s') for e in entities]  # Remove plurals
        entities = list(set(entities))  # Remove duplicates
        
        # Filter out common words and action verbs
        stop_words = ['the', 'and', 'or', 'for', 'with', 'that', 'this', 'it', 'a', 'an',
                     'create', 'read', 'update', 'delete', 'get', 'set', 'add', 'remove',
                     'new', 'all', 'any', 'some', 'make', 'build', 'i', 'mcp', 'can', 
                     'able', 'should', 'would', 'could', 'including', 'like', 'such',
                     'individual', 'each', 'every', 'single', 'multiple', 'several']
        entities = [e for e in entities if e not in stop_words and len(e) > 2]
        
        # Prioritize by frequency and relevance
        entity_counts = {}
        for entity in entities:
            count = req_lower.count(entity)
            entity_counts[entity] = count
        
        # Sort by frequency
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [entity for entity, _ in sorted_entities][:5]  # Return top 5
    
    def _extract_operations(self, req_lower: str) -> List[str]:
        """Extract specific operations mentioned"""
        operations = []
        
        # Common operation patterns
        operation_patterns = {
            'listing': ['list', 'show all', 'get all', 'display all'],
            'searching': ['search', 'find', 'query', 'lookup'],
            'filtering': ['filter', 'where', 'matching', 'with'],
            'sorting': ['sort', 'order by', 'arrange'],
            'aggregating': ['sum', 'count', 'average', 'total'],
            'comparing': ['compare', 'diff', 'versus', 'between'],
            'converting': ['convert', 'transform', 'change to'],
            'validating': ['validate', 'check', 'verify', 'ensure']
        }
        
        for op_type, patterns in operation_patterns.items():
            if any(pattern in req_lower for pattern in patterns):
                operations.append(op_type)
        
        return operations
    
    def _extract_attributes(self, requirements: str) -> List[str]:
        """Extract attributes or properties mentioned"""
        attributes = []
        
        # Common attribute patterns
        attr_patterns = [
            r'by (\w+)',
            r'with (\w+)',
            r'having (\w+)',
            r'where (\w+)',
            r'(\w+) status',
            r'(\w+) type',
            r'(\w+) name',
            r'(\w+) id'
        ]
        
        for pattern in attr_patterns:
            matches = re.findall(pattern, requirements.lower())
            attributes.extend(matches)
        
        return list(set(attributes))[:10]
    
    def _extract_technical_terms(self, requirements: str) -> List[str]:
        """Extract technical terms and acronyms"""
        terms = []
        
        # Find acronyms (2-5 uppercase letters)
        acronyms = re.findall(r'\b[A-Z]{2,5}\b', requirements)
        terms.extend(acronyms)
        
        # Find technical patterns
        tech_patterns = [
            r'[A-Z][a-z]+(?:[A-Z][a-z]+)+',  # CamelCase
            r'\w+\.\w+',  # file.extension
            r'\w+://\w+',  # protocol://
            r'\w+@\w+',  # email-like
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, requirements)
            terms.extend(matches)
        
        return list(set(terms))
    
    def _generate_tool_suggestions(
        self, 
        domain: str, 
        actions: List[str], 
        entities: List[str], 
        operations: List[str],
        requirements: str
    ) -> List[Dict[str, any]]:
        """Generate suggested tools based on analysis"""
        tools = []
        tool_names_used = set()
        
        # Check for specific service mentions in requirements
        req_lower = requirements.lower()
        
        # Service-specific tool generation - expanded to cover more services
        if any(service in req_lower for service in ['github', 'gitlab']):
            tools.extend([
                {'name': 'list_repositories', 'type': 'list', 'entity': 'repo', 'likely_params': ['org', 'filter']},
                {'name': 'create_issue', 'type': 'create', 'entity': 'issue', 'likely_params': ['repo', 'title', 'body']},
                {'name': 'get_pull_requests', 'type': 'list', 'entity': 'pr', 'likely_params': ['repo', 'state']},
                {'name': 'manage_workflow', 'type': 'manage', 'entity': 'workflow', 'likely_params': ['repo', 'action']},
                {'name': 'search_code', 'type': 'search', 'entity': 'code', 'likely_params': ['query', 'scope']},
                {'name': 'get_commits', 'type': 'list', 'entity': 'commit', 'likely_params': ['repo', 'branch']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['slack', 'discord', 'teams', 'mattermost']):
            tools.extend([
                {'name': 'send_message', 'type': 'send', 'entity': 'message', 'likely_params': ['channel', 'text']},
                {'name': 'list_channels', 'type': 'list', 'entity': 'channel', 'likely_params': ['workspace']},
                {'name': 'get_channel_history', 'type': 'read', 'entity': 'history', 'likely_params': ['channel', 'limit']},
                {'name': 'manage_users', 'type': 'manage', 'entity': 'user', 'likely_params': ['user_id', 'action']},
                {'name': 'create_channel', 'type': 'create', 'entity': 'channel', 'likely_params': ['name', 'type']},
                {'name': 'upload_file', 'type': 'upload', 'entity': 'file', 'likely_params': ['channel', 'file_path']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['notion', 'linear', 'confluence', 'jira']):
            tools.extend([
                {'name': 'create_page', 'type': 'create', 'entity': 'page', 'likely_params': ['title', 'content', 'parent']},
                {'name': 'search_workspace', 'type': 'search', 'entity': 'content', 'likely_params': ['query', 'type']},
                {'name': 'update_page', 'type': 'update', 'entity': 'page', 'likely_params': ['page_id', 'updates']},
                {'name': 'list_projects', 'type': 'list', 'entity': 'project', 'likely_params': ['workspace', 'filter']},
                {'name': 'manage_tasks', 'type': 'manage', 'entity': 'task', 'likely_params': ['task_id', 'action']},
                {'name': 'export_data', 'type': 'export', 'entity': 'data', 'likely_params': ['format', 'filters']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['postgresql', 'postgres', 'mysql', 'mariadb']):
            tools.extend([
                {'name': 'execute_query', 'type': 'query', 'entity': 'database', 'likely_params': ['query', 'params']},
                {'name': 'list_tables', 'type': 'list', 'entity': 'table', 'likely_params': ['schema', 'pattern']},
                {'name': 'get_schema', 'type': 'read', 'entity': 'schema', 'likely_params': ['table_name']},
                {'name': 'backup_database', 'type': 'backup', 'entity': 'database', 'likely_params': ['output_path']},
                {'name': 'manage_indexes', 'type': 'manage', 'entity': 'index', 'likely_params': ['table', 'action']},
                {'name': 'analyze_performance', 'type': 'analyze', 'entity': 'query', 'likely_params': ['query_id']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['mongodb', 'mongo', 'dynamodb', 'cassandra']):
            tools.extend([
                {'name': 'insert_document', 'type': 'create', 'entity': 'document', 'likely_params': ['collection', 'data']},
                {'name': 'find_documents', 'type': 'search', 'entity': 'document', 'likely_params': ['collection', 'filter']},
                {'name': 'update_document', 'type': 'update', 'entity': 'document', 'likely_params': ['collection', 'filter', 'update']},
                {'name': 'aggregate_data', 'type': 'aggregate', 'entity': 'data', 'likely_params': ['collection', 'pipeline']},
                {'name': 'list_collections', 'type': 'list', 'entity': 'collection', 'likely_params': ['database']},
                {'name': 'manage_indexes', 'type': 'manage', 'entity': 'index', 'likely_params': ['collection', 'action']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['redis', 'memcached', 'cache']):
            tools.extend([
                {'name': 'set_value', 'type': 'write', 'entity': 'key', 'likely_params': ['key', 'value', 'ttl']},
                {'name': 'get_value', 'type': 'read', 'entity': 'key', 'likely_params': ['key']},
                {'name': 'delete_key', 'type': 'delete', 'entity': 'key', 'likely_params': ['key']},
                {'name': 'list_keys', 'type': 'list', 'entity': 'key', 'likely_params': ['pattern']},
                {'name': 'manage_pub_sub', 'type': 'manage', 'entity': 'channel', 'likely_params': ['channel', 'action']},
                {'name': 'flush_cache', 'type': 'flush', 'entity': 'cache', 'likely_params': ['pattern']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['elasticsearch', 'elastic', 'solr', 'opensearch']):
            tools.extend([
                {'name': 'index_document', 'type': 'index', 'entity': 'document', 'likely_params': ['index', 'document']},
                {'name': 'search_documents', 'type': 'search', 'entity': 'document', 'likely_params': ['index', 'query']},
                {'name': 'aggregate_data', 'type': 'aggregate', 'entity': 'data', 'likely_params': ['index', 'aggregation']},
                {'name': 'manage_mappings', 'type': 'manage', 'entity': 'mapping', 'likely_params': ['index', 'mapping']},
                {'name': 'analyze_text', 'type': 'analyze', 'entity': 'text', 'likely_params': ['text', 'analyzer']},
                {'name': 'list_indices', 'type': 'list', 'entity': 'index', 'likely_params': ['pattern']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['stripe', 'paypal', 'square', 'payment']):
            tools.extend([
                {'name': 'create_payment', 'type': 'create', 'entity': 'payment', 'likely_params': ['amount', 'currency', 'method']},
                {'name': 'list_transactions', 'type': 'list', 'entity': 'transaction', 'likely_params': ['start_date', 'end_date']},
                {'name': 'refund_payment', 'type': 'refund', 'entity': 'payment', 'likely_params': ['payment_id', 'amount']},
                {'name': 'manage_customers', 'type': 'manage', 'entity': 'customer', 'likely_params': ['customer_id', 'action']},
                {'name': 'create_subscription', 'type': 'create', 'entity': 'subscription', 'likely_params': ['customer_id', 'plan']},
                {'name': 'generate_invoice', 'type': 'generate', 'entity': 'invoice', 'likely_params': ['customer_id', 'items']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['aws', 's3', 'ec2', 'lambda']):
            tools.extend([
                {'name': 'list_resources', 'type': 'list', 'entity': 'resource', 'likely_params': ['service', 'region']},
                {'name': 'manage_instance', 'type': 'manage', 'entity': 'instance', 'likely_params': ['instance_id', 'action']},
                {'name': 'upload_to_s3', 'type': 'upload', 'entity': 'file', 'likely_params': ['bucket', 'key', 'file_path']},
                {'name': 'invoke_function', 'type': 'invoke', 'entity': 'function', 'likely_params': ['function_name', 'payload']},
                {'name': 'get_metrics', 'type': 'read', 'entity': 'metrics', 'likely_params': ['service', 'timeframe']},
                {'name': 'manage_security', 'type': 'manage', 'entity': 'security', 'likely_params': ['resource_id', 'rules']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['docker', 'kubernetes', 'k8s', 'container']):
            tools.extend([
                {'name': 'list_containers', 'type': 'list', 'entity': 'container', 'likely_params': ['filter', 'all']},
                {'name': 'manage_container', 'type': 'manage', 'entity': 'container', 'likely_params': ['container_id', 'action']},
                {'name': 'deploy_application', 'type': 'deploy', 'entity': 'application', 'likely_params': ['manifest', 'namespace']},
                {'name': 'get_logs', 'type': 'read', 'entity': 'logs', 'likely_params': ['container_id', 'lines']},
                {'name': 'scale_deployment', 'type': 'scale', 'entity': 'deployment', 'likely_params': ['deployment', 'replicas']},
                {'name': 'monitor_health', 'type': 'monitor', 'entity': 'health', 'likely_params': ['resource', 'interval']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['jenkins', 'circleci', 'github actions', 'ci/cd']):
            tools.extend([
                {'name': 'trigger_build', 'type': 'trigger', 'entity': 'build', 'likely_params': ['job', 'parameters']},
                {'name': 'list_jobs', 'type': 'list', 'entity': 'job', 'likely_params': ['folder', 'filter']},
                {'name': 'get_build_status', 'type': 'read', 'entity': 'status', 'likely_params': ['job', 'build_number']},
                {'name': 'manage_pipeline', 'type': 'manage', 'entity': 'pipeline', 'likely_params': ['pipeline_id', 'action']},
                {'name': 'view_artifacts', 'type': 'view', 'entity': 'artifact', 'likely_params': ['job', 'build_number']},
                {'name': 'configure_job', 'type': 'configure', 'entity': 'job', 'likely_params': ['job_name', 'config']}
            ])
            return tools[:6]
        elif any(service in req_lower for service in ['prometheus', 'grafana', 'datadog', 'monitoring']):
            tools.extend([
                {'name': 'query_metrics', 'type': 'query', 'entity': 'metrics', 'likely_params': ['query', 'timeframe']},
                {'name': 'create_alert', 'type': 'create', 'entity': 'alert', 'likely_params': ['condition', 'threshold']},
                {'name': 'list_dashboards', 'type': 'list', 'entity': 'dashboard', 'likely_params': ['folder']},
                {'name': 'export_data', 'type': 'export', 'entity': 'data', 'likely_params': ['format', 'timeframe']},
                {'name': 'manage_annotations', 'type': 'manage', 'entity': 'annotation', 'likely_params': ['dashboard', 'action']},
                {'name': 'analyze_trends', 'type': 'analyze', 'entity': 'trend', 'likely_params': ['metric', 'period']}
            ])
            return tools[:6]
        
        # If we have good entities, use them
        if entities:
            primary_entity = entities[0]
            
            # Generate CRUD tools for primary entity
            if 'create' in actions:
                tool_name = f'create_{primary_entity}'
                if tool_name not in tool_names_used:
                    tools.append({
                        'name': tool_name,
                        'type': 'create',
                        'entity': primary_entity,
                        'likely_params': [f'{primary_entity}_data', 'validate']
                    })
                    tool_names_used.add(tool_name)
            
            if 'read' in actions or 'listing' in operations:
                # Get single
                tool_name = f'get_{primary_entity}'
                if tool_name not in tool_names_used:
                    tools.append({
                        'name': tool_name,
                        'type': 'read',
                        'entity': primary_entity,
                        'likely_params': [f'{primary_entity}_id']
                    })
                    tool_names_used.add(tool_name)
                
                # List multiple
                tool_name = f'list_{primary_entity}s'
                if tool_name not in tool_names_used:
                    tools.append({
                        'name': tool_name,
                        'type': 'list',
                        'entity': primary_entity,
                        'likely_params': ['limit', 'offset', 'filter']
                    })
                    tool_names_used.add(tool_name)
            
            if 'update' in actions:
                tool_name = f'update_{primary_entity}'
                if tool_name not in tool_names_used:
                    tools.append({
                        'name': tool_name,
                        'type': 'update',
                        'entity': primary_entity,
                        'likely_params': [f'{primary_entity}_id', 'updates']
                    })
                    tool_names_used.add(tool_name)
            
            if 'delete' in actions:
                tool_name = f'delete_{primary_entity}'
                if tool_name not in tool_names_used:
                    tools.append({
                        'name': tool_name,
                        'type': 'delete',
                        'entity': primary_entity,
                        'likely_params': [f'{primary_entity}_id', 'confirm']
                    })
                    tool_names_used.add(tool_name)
        
        # Add action-specific tools
        if 'monitor' in actions:
            entity_to_monitor = entities[0] if entities else domain
            tool_name = f'monitor_{entity_to_monitor}'
            if tool_name not in tool_names_used:
                tools.append({
                    'name': tool_name,
                    'type': 'monitor',
                    'entity': entity_to_monitor,
                    'likely_params': ['target', 'interval', 'threshold']
                })
                tool_names_used.add(tool_name)
        
        if 'process' in actions or 'analyze' in actions:
            entity_to_process = entities[0] if entities else 'data'
            tool_name = f'analyze_{entity_to_process}'
            if tool_name not in tool_names_used:
                tools.append({
                    'name': tool_name,
                    'type': 'process',
                    'entity': entity_to_process,
                    'likely_params': ['input_data', 'analysis_type', 'options']
                })
                tool_names_used.add(tool_name)
        
        if 'manage' in actions and entities:
            # Add control tool for management
            tool_name = f'control_{entities[0]}'
            if tool_name not in tool_names_used:
                tools.append({
                    'name': tool_name,
                    'type': 'control',
                    'entity': entities[0],
                    'likely_params': [f'{entities[0]}_id', 'action', 'parameters']
                })
                tool_names_used.add(tool_name)
        
        # If no tools generated, create generic ones based on domain
        if not tools:
            tools = self._generate_fallback_tools(domain)
        
        return tools[:6]  # Maximum 6 tools
    
    def _generate_fallback_tools(self, domain: str) -> List[Dict[str, any]]:
        """Generate fallback tools based on MCP domain"""
        if domain == 'api_integration':
            return [
                {'name': 'authenticate', 'type': 'auth', 'entity': 'api', 'likely_params': ['credentials', 'token_type']},
                {'name': 'make_request', 'type': 'request', 'entity': 'endpoint', 'likely_params': ['method', 'url', 'data']},
                {'name': 'handle_response', 'type': 'process', 'entity': 'response', 'likely_params': ['response', 'format']}
            ]
        elif domain == 'database':
            return [
                {'name': 'execute_query', 'type': 'query', 'entity': 'database', 'likely_params': ['query', 'params']},
                {'name': 'get_schema', 'type': 'read', 'entity': 'schema', 'likely_params': ['table_name']},
                {'name': 'list_tables', 'type': 'list', 'entity': 'table', 'likely_params': ['database']}
            ]
        elif domain == 'file_system':
            return [
                {'name': 'read_file', 'type': 'read', 'entity': 'file', 'likely_params': ['path', 'encoding']},
                {'name': 'write_file', 'type': 'write', 'entity': 'file', 'likely_params': ['path', 'content']},
                {'name': 'list_directory', 'type': 'list', 'entity': 'directory', 'likely_params': ['path', 'pattern']}
            ]
        elif domain == 'development_tools':
            return [
                {'name': 'get_commits', 'type': 'list', 'entity': 'commit', 'likely_params': ['repo', 'branch']},
                {'name': 'create_pull_request', 'type': 'create', 'entity': 'pr', 'likely_params': ['title', 'body', 'base']},
                {'name': 'list_issues', 'type': 'list', 'entity': 'issue', 'likely_params': ['repo', 'state']}
            ]
        elif domain == 'communication':
            return [
                {'name': 'send_message', 'type': 'send', 'entity': 'message', 'likely_params': ['channel', 'text']},
                {'name': 'list_channels', 'type': 'list', 'entity': 'channel', 'likely_params': ['workspace']},
                {'name': 'get_user_info', 'type': 'read', 'entity': 'user', 'likely_params': ['user_id']}
            ]
        elif domain == 'productivity':
            return [
                {'name': 'create_task', 'type': 'create', 'entity': 'task', 'likely_params': ['title', 'description', 'project']},
                {'name': 'list_projects', 'type': 'list', 'entity': 'project', 'likely_params': ['workspace']},
                {'name': 'update_task_status', 'type': 'update', 'entity': 'task', 'likely_params': ['task_id', 'status']}
            ]
        elif domain == 'web_tools':
            return [
                {'name': 'scrape_page', 'type': 'scrape', 'entity': 'webpage', 'likely_params': ['url', 'selector']},
                {'name': 'search_web', 'type': 'search', 'entity': 'results', 'likely_params': ['query', 'count']},
                {'name': 'take_screenshot', 'type': 'capture', 'entity': 'screenshot', 'likely_params': ['url', 'viewport']}
            ]
        elif domain == 'cloud_services':
            return [
                {'name': 'list_resources', 'type': 'list', 'entity': 'resource', 'likely_params': ['service', 'region']},
                {'name': 'deploy_function', 'type': 'deploy', 'entity': 'function', 'likely_params': ['code', 'runtime']},
                {'name': 'get_metrics', 'type': 'read', 'entity': 'metrics', 'likely_params': ['resource_id', 'timeframe']}
            ]
        else:
            # Generic tools for unknown domains
            return [
                {'name': 'fetch_data', 'type': 'read', 'entity': 'data', 'likely_params': ['source', 'filter']},
                {'name': 'process_data', 'type': 'process', 'entity': 'data', 'likely_params': ['input', 'operation']},
                {'name': 'store_result', 'type': 'write', 'entity': 'result', 'likely_params': ['data', 'destination']}
            ]