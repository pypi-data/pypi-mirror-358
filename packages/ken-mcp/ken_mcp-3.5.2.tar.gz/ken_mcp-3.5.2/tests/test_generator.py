"""Integration tests for KEN-MCP generator"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from ken_mcp.core.orchestrator import generate_mcp_server
from ken_mcp.core.analyzer import analyze_and_plan


class TestGeneratorIntegration:
    """Test the main generator integration"""
    
    def test_analyze_requirements_basic_integration(self):
        """Test basic requirements analysis integration"""
        plan = analyze_and_plan("Create a simple calculator MCP")
        
        assert plan is not None
        assert "calculator" in plan.description.lower()
        assert len(plan.tools) == 3
        assert plan.original_requirements == "Create a simple calculator MCP"
    
    def test_analyze_requirements_with_resources_integration(self):
        """Test requirements analysis with resources"""
        plan = analyze_and_plan("Build a file manager", include_resources=True)
        
        assert plan is not None
        assert len(plan.resources) > 0
        assert len(plan.tools) == 3
    
    def test_analyze_requirements_with_prompts_integration(self):
        """Test requirements analysis with prompts"""
        plan = analyze_and_plan("Create a help system", include_prompts=True)
        
        assert plan is not None
        assert len(plan.prompts) > 0
        assert len(plan.tools) == 3
    
    @pytest.mark.asyncio
    async def test_generate_mcp_server_basic_integration(self):
        """Test basic MCP server generation integration"""
        # Create mock context
        mock_context = MagicMock()
        mock_context.messages = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await generate_mcp_server(
                ctx=mock_context,
                requirements="Create a simple calculator MCP",
                project_name="test-calc",
                output_dir=temp_dir,
                include_resources=False,
                include_prompts=False
            )
            
            assert result["success"] is True
            assert "test-calc" in result["project_path"]
            assert result["tools_generated"] >= 3
            
            # Check that files were created
            project_path = Path(result["project_path"])
            assert project_path.exists()
            assert (project_path / "server.py").exists()
            assert (project_path / "README.md").exists()
    
    @pytest.mark.asyncio
    async def test_generate_mcp_server_with_resources_integration(self):
        """Test MCP server generation with resources"""
        mock_context = MagicMock()
        mock_context.messages = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await generate_mcp_server(
                ctx=mock_context,
                requirements="Build a file manager with resource access",
                project_name="test-files",
                output_dir=temp_dir,
                include_resources=True,
                include_prompts=False
            )
            
            assert result["success"] is True
            assert result["resources_generated"] > 0
    
    @pytest.mark.asyncio
    async def test_generate_mcp_server_complex_requirements_integration(self):
        """Test MCP server generation with complex requirements"""
        mock_context = MagicMock()
        mock_context.messages = []
        
        complex_req = "Create an advanced task management system with priority handling, due dates, and progress tracking"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await generate_mcp_server(
                ctx=mock_context,
                requirements=complex_req,
                project_name="task-manager",
                output_dir=temp_dir,
                include_resources=True,
                include_prompts=True
            )
            
            assert result["success"] is True
            assert result["tools_generated"] >= 3
            assert result["resources_generated"] > 0
            assert result["prompts_generated"] > 0
    
    def test_edge_case_empty_requirements(self):
        """Test handling of empty requirements"""
        plan = analyze_and_plan("")
        
        assert plan is not None
        assert plan.original_requirements == ""
        assert len(plan.tools) == 3  # Should still generate default tools
    
    def test_edge_case_very_long_requirements(self):
        """Test handling of very long requirements"""
        long_req = "Build a comprehensive system " * 100
        plan = analyze_and_plan(long_req)
        
        assert plan is not None
        assert plan.original_requirements == long_req
        assert len(plan.description) < 1000  # Should be truncated reasonably