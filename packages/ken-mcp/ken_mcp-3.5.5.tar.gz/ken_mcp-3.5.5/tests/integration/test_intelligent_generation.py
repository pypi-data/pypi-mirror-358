#!/usr/bin/env python3
"""
Test the enhanced intelligent MCP generation
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the MCP directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ken_mcp.core.models import ProjectConfig
from ken_mcp.core.orchestrator import generate_mcp_server
from ken_mcp.core.analyzer import analyze_and_plan
from ken_mcp.core.requirement_parser import RequirementParser


class MockContext:
    """Mock context for testing"""
    async def info(self, msg):
        print(f"[INFO] {msg}")
    
    async def report_progress(self, current, total, msg):
        print(f"[{current}/{total}] {msg}")


async def test_requirement_parsing():
    """Test the requirement parser with various examples"""
    print("\n" + "="*70)
    print("TESTING REQUIREMENT PARSER")
    print("="*70)
    
    test_cases = [
        "Create an MCP for managing smart home devices like lights, thermostats, and sensors",
        "Build an MCP that analyzes DNA sequences and finds mutations",
        "I need an MCP to monitor Bitcoin and Ethereum prices and send alerts",
        "Create an MCP for tracking workout routines and fitness progress",
        "Build an MCP that interfaces with Kubernetes to manage deployments",
        "I want an MCP that can scrape news articles and summarize them",
        "Create an MCP for managing a restaurant's orders and inventory"
    ]
    
    parser = RequirementParser()
    
    for req in test_cases:
        print(f"\n📝 Requirements: {req}")
        parsed = parser.parse(req)
        
        print(f"   Domain: {parsed.domain}")
        print(f"   Actions: {', '.join(parsed.primary_actions)}")
        print(f"   Entities: {', '.join(parsed.entities)}")
        print(f"   Suggested tools:")
        for tool in parsed.suggested_tools:
            print(f"      - {tool['name']} ({tool['type']})")


async def test_plan_generation():
    """Test the enhanced plan generation"""
    print("\n" + "="*70)
    print("TESTING ENHANCED PLAN GENERATION")
    print("="*70)
    
    test_cases = [
        {
            "req": "Create an MCP for managing smart home devices",
            "name": "smart-home-mcp"
        },
        {
            "req": "Build an MCP that tracks cryptocurrency portfolio performance",
            "name": "crypto-tracker-mcp"
        },
        {
            "req": "I need an MCP for processing and analyzing log files",
            "name": "log-analyzer-mcp"
        }
    ]
    
    for test in test_cases:
        print(f"\n📦 Generating plan for: {test['name']}")
        print(f"   Requirements: {test['req']}")
        
        plan = analyze_and_plan(test['req'])
        
        print(f"\n   Analysis context:")
        if plan.analysis_context:
            print(f"      Domain: {plan.analysis_context.get('domain')}")
            print(f"      Actions: {', '.join(plan.analysis_context.get('primary_actions', []))}")
        
        print(f"\n   Generated tools:")
        for tool in plan.tools:
            print(f"      - {tool.name}")
            print(f"        Type: {tool.implementation}")
            print(f"        Parameters: {', '.join(p.name for p in tool.parameters)}")


async def test_full_generation():
    """Test full MCP generation with intelligent scaffolding"""
    print("\n" + "="*70)
    print("TESTING FULL MCP GENERATION")
    print("="*70)
    
    # Test case: Smart home controller
    config = ProjectConfig(
        requirements="Create an MCP for controlling smart home devices including lights, thermostats, and security cameras. It should be able to list all devices, control individual devices, set up automation rules, and monitor device status.",
        project_name="smart-home-controller",
        output_dir="test_intelligent_mcps"
    )
    
    print(f"\n🏠 Generating: {config.project_name}")
    print(f"   Requirements: {config.requirements[:100]}...")
    
    ctx = MockContext()
    result = await generate_mcp_server(ctx, config)
    
    if result.success:
        print(f"\n   ✅ Generated successfully!")
        print(f"   Path: {result.project_path}")
        print(f"   Tools: {result.tools_generated}")
        
        # Check the generated server.py
        server_file = result.project_path / "server.py"
        if server_file.exists():
            content = server_file.read_text()
            
            # Look for intelligent tool names
            print(f"\n   Generated tools:")
            import re
            tool_matches = re.findall(r'async def (\w+)\(', content)
            for tool in tool_matches:
                print(f"      - {tool}")
            
            # Check for analysis context
            if "Analysis Results:" in content:
                print(f"\n   ✅ Analysis context included in generated code")


async def test_diverse_domains():
    """Test generation across diverse domains"""
    print("\n" + "="*70)
    print("TESTING DIVERSE DOMAINS")
    print("="*70)
    
    domains = [
        ("Biology", "Create an MCP for analyzing protein sequences and predicting structures"),
        ("Gaming", "Build an MCP for managing game server instances and player statistics"),
        ("Education", "I need an MCP for creating and grading online quizzes"),
        ("Healthcare", "Create an MCP for managing patient appointments and medical records"),
        ("Logistics", "Build an MCP for tracking shipments and optimizing delivery routes")
    ]
    
    for domain_name, requirements in domains:
        print(f"\n🔬 Testing {domain_name} domain:")
        plan = analyze_and_plan(requirements)
        
        print(f"   Detected domain: {plan.analysis_context.get('domain') if plan.analysis_context else 'unknown'}")
        print(f"   Generated {len(plan.tools)} tools:")
        for tool in plan.tools[:3]:  # Show first 3
            print(f"      - {tool.name}")


async def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Intelligent MCP Generation\n")
    
    await test_requirement_parsing()
    await test_plan_generation()
    await test_full_generation()
    await test_diverse_domains()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())