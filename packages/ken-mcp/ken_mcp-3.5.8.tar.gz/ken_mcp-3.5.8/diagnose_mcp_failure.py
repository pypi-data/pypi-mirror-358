#!/usr/bin/env python3
"""
MCP Failure Diagnostic Script
Comprehensive diagnostic tool to identify why MCP servers fail to load in Claude Code
"""

import sys
import os
import subprocess
import json
import ast
import asyncio
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# Ensure we don't pollute stdout ourselves
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

class MCPDiagnostics:
    def __init__(self, mcp_path: str):
        self.mcp_path = Path(mcp_path).resolve()
        self.server_path = self.mcp_path / "server.py"
        self.pyproject_path = self.mcp_path / "pyproject.toml"
        self.results = []
        self.errors = []
        self.warnings = []
        
    def add_result(self, category: str, test: str, passed: bool, details: str = ""):
        """Add a diagnostic result"""
        status = "✅" if passed else "❌"
        self.results.append(f"{status} [{category}] {test}")
        if details:
            self.results.append(f"   → {details}")
        if not passed:
            self.errors.append(f"[{category}] {test}: {details}")
            
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(f"⚠️  {message}")
        
    def run_diagnostics(self):
        """Run all diagnostic checks"""
        print("🔍 MCP Failure Diagnostics")
        print(f"📁 Checking: {self.mcp_path}")
        print("=" * 60)
        
        # Check if paths exist
        if not self.mcp_path.exists():
            self.add_result("PATH", "MCP directory exists", False, f"Directory not found: {self.mcp_path}")
            return
        
        if not self.server_path.exists():
            self.add_result("PATH", "server.py exists", False, "server.py not found in MCP directory")
            return
        
        self.add_result("PATH", "MCP directory exists", True)
        self.add_result("PATH", "server.py exists", True)
        
        # Run all checks
        self.check_python_version()
        self.check_dependencies()
        self.check_server_syntax()
        self.check_stdout_pollution()
        self.check_logging_config()
        self.check_fastmcp_api_usage()
        self.check_import_issues()
        self.test_server_execution()
        self.test_json_rpc_compliance()
        self.check_permissions()
        
        # Generate report
        self.generate_report()
        
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major >= 3 and version.minor >= 10:
            self.add_result("PYTHON", "Python version", True, f"Python {version_str}")
        else:
            self.add_result("PYTHON", "Python version", False, f"Python {version_str} (requires 3.10+)")
            
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        try:
            # Check FastMCP
            import fastmcp
            self.add_result("DEPS", "FastMCP installed", True, f"Version: {getattr(fastmcp, '__version__', 'unknown')}")
        except ImportError:
            self.add_result("DEPS", "FastMCP installed", False, "FastMCP not found. Install with: pip install fastmcp")
            
        # Check pyproject.toml dependencies
        if self.pyproject_path.exists():
            try:
                import tomli
                with open(self.pyproject_path, 'rb') as f:
                    pyproject = tomli.load(f)
                deps = pyproject.get('project', {}).get('dependencies', [])
                
                for dep in deps:
                    dep_name = dep.split('[')[0].split('>=')[0].split('==')[0].strip()
                    try:
                        __import__(dep_name.replace('-', '_'))
                        self.add_result("DEPS", f"Dependency: {dep_name}", True)
                    except ImportError:
                        self.add_result("DEPS", f"Dependency: {dep_name}", False, f"Not installed")
            except ImportError:
                self.add_warning("tomli not installed, skipping pyproject.toml parsing")
            except Exception as e:
                self.add_warning(f"Failed to parse pyproject.toml: {e}")
                
    def check_server_syntax(self):
        """Check server.py for syntax errors"""
        try:
            with open(self.server_path, 'r') as f:
                code = f.read()
            
            # Try to compile the code
            compile(code, str(self.server_path), 'exec')
            self.add_result("SYNTAX", "server.py syntax", True)
            
            # Parse AST for deeper analysis
            tree = ast.parse(code)
            self.analyze_ast(tree)
            
        except SyntaxError as e:
            self.add_result("SYNTAX", "server.py syntax", False, f"Line {e.lineno}: {e.msg}")
        except Exception as e:
            self.add_result("SYNTAX", "server.py syntax", False, str(e))
            
    def analyze_ast(self, tree):
        """Analyze AST for common issues"""
        class PrintChecker(ast.NodeVisitor):
            def __init__(self):
                self.print_calls = []
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    self.print_calls.append(node.lineno)
                self.generic_visit(node)
                
        checker = PrintChecker()
        checker.visit(tree)
        
        if checker.print_calls:
            self.add_result("STDOUT", "No print() statements", False, 
                          f"Found print() at lines: {', '.join(map(str, checker.print_calls))}")
            self.add_warning("print() statements will break MCP protocol! Use logger.info() instead")
        else:
            self.add_result("STDOUT", "No print() statements", True)
            
    def check_stdout_pollution(self):
        """Check for potential stdout pollution"""
        with open(self.server_path, 'r') as f:
            content = f.read()
            
        # Check for stdout redirect
        if "sys.stdout = sys.stderr" in content:
            self.add_result("STDOUT", "Stdout redirection present", True)
        else:
            self.add_warning("No stdout redirection found - consider adding to prevent pollution")
            
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'print\s*\(', "print() function calls"),
            (r'sys\.stdout\.write', "Direct stdout writes"),
            (r'pprint\s*\(', "pprint() calls"),
        ]
        
        for pattern, description in dangerous_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.add_result("STDOUT", f"No {description}", False, f"Found {len(matches)} instances")
                
    def check_logging_config(self):
        """Check logging configuration"""
        with open(self.server_path, 'r') as f:
            content = f.read()
            
        # Check for proper logging setup
        if "logging.basicConfig" in content and "stream=sys.stderr" in content:
            self.add_result("LOGGING", "Logging to stderr", True)
        else:
            self.add_result("LOGGING", "Logging to stderr", False, 
                          "Logging not configured to stderr - will pollute stdout")
            
    def check_fastmcp_api_usage(self):
        """Check for correct FastMCP API usage"""
        with open(self.server_path, 'r') as f:
            content = f.read()
            
        # Check for common API mistakes
        api_issues = []
        
        if "tool.function" in content:
            api_issues.append("Using 'tool.function' instead of 'tool.fn'")
        if "_tools" in content:
            api_issues.append("Accessing private '_tools' attribute")
        if "_resources" in content:
            api_issues.append("Accessing private '_resources' attribute")
        if "_prompts" in content:
            api_issues.append("Accessing private '_prompts' attribute")
            
        if api_issues:
            self.add_result("API", "FastMCP API usage", False, "; ".join(api_issues))
        else:
            self.add_result("API", "FastMCP API usage", True)
            
    def check_import_issues(self):
        """Check for import issues"""
        try:
            # Temporarily redirect stdout
            old_stdout = sys.stdout
            sys.stdout = sys.stderr
            
            # Try to import the server module
            spec = importlib.util.spec_from_file_location("test_server", self.server_path)
            module = importlib.util.module_from_spec(spec)
            
            # Execute in isolated namespace
            spec.loader.exec_module(module)
            
            sys.stdout = old_stdout
            self.add_result("IMPORT", "Server imports successfully", True)
            
        except Exception as e:
            sys.stdout = old_stdout
            self.add_result("IMPORT", "Server imports successfully", False, str(e))
            
    def test_server_execution(self):
        """Test direct server execution"""
        try:
            # Run server with a timeout
            result = subprocess.run(
                [sys.executable, str(self.server_path)],
                capture_output=True,
                text=True,
                timeout=2,
                env={**os.environ, "MCP_TEST_MODE": "1"}
            )
            
            # Check if it started without errors
            if result.returncode == 0 or "Server started" in result.stderr:
                self.add_result("EXEC", "Server starts without errors", True)
            else:
                self.add_result("EXEC", "Server starts without errors", False, 
                              f"Exit code: {result.returncode}")
                if result.stderr:
                    self.add_warning(f"Stderr: {result.stderr[:200]}")
                    
        except subprocess.TimeoutExpired:
            # Timeout is expected for a running server
            self.add_result("EXEC", "Server starts without errors", True, "Server running (timeout expected)")
        except Exception as e:
            self.add_result("EXEC", "Server starts without errors", False, str(e))
            
    def test_json_rpc_compliance(self):
        """Test JSON-RPC compliance"""
        try:
            # Create a simple JSON-RPC request
            test_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"capabilities": {}},
                "id": 1
            }
            
            # Run server with input
            proc = subprocess.Popen(
                [sys.executable, str(self.server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send request
            proc.stdin.write(json.dumps(test_request) + '\n')
            proc.stdin.flush()
            
            # Wait briefly for response
            import time
            time.sleep(0.5)
            
            # Terminate
            proc.terminate()
            stdout, stderr = proc.communicate(timeout=1)
            
            # Check if stdout contains valid JSON
            if stdout.strip():
                try:
                    response = json.loads(stdout.strip().split('\n')[0])
                    if "jsonrpc" in response:
                        self.add_result("JSON-RPC", "Valid JSON-RPC response", True)
                    else:
                        self.add_result("JSON-RPC", "Valid JSON-RPC response", False, "Missing jsonrpc field")
                except json.JSONDecodeError:
                    self.add_result("JSON-RPC", "Valid JSON-RPC response", False, 
                                  "Invalid JSON in stdout (pollution detected)")
            else:
                self.add_result("JSON-RPC", "Valid JSON-RPC response", False, "No response received")
                
        except Exception as e:
            self.add_result("JSON-RPC", "Valid JSON-RPC response", False, str(e))
            
    def check_permissions(self):
        """Check file permissions"""
        if os.access(self.server_path, os.X_OK):
            self.add_result("PERMS", "server.py is executable", True)
        else:
            self.add_result("PERMS", "server.py is executable", False, "Not executable")
            
    def generate_report(self):
        """Generate final diagnostic report"""
        print("\n📊 DIAGNOSTIC RESULTS")
        print("=" * 60)
        
        for result in self.results:
            print(result)
            
        if self.warnings:
            print("\n⚠️  WARNINGS")
            print("-" * 60)
            for warning in self.warnings:
                print(warning)
                
        if self.errors:
            print("\n❌ FAILURES SUMMARY")
            print("-" * 60)
            for error in self.errors:
                print(f"  • {error}")
                
            print("\n🔧 RECOMMENDED FIXES")
            print("-" * 60)
            
            # Generate specific recommendations
            if any("print()" in e for e in self.errors):
                print("  1. Replace all print() with logger.info()")
                print("     Find: print(")
                print("     Replace: logger.info(")
                
            if any("FastMCP" in e for e in self.errors):
                print("  2. Install FastMCP: pip install fastmcp")
                
            if any("tool.function" in e for e in self.errors):
                print("  3. Fix API usage:")
                print("     Change: tool.function → tool.fn")
                print("     Change: resource.function → resource.fn")
                
            if any("stderr" in e for e in self.errors):
                print("  4. Add logging configuration at top of server.py:")
                print("     logging.basicConfig(level=logging.INFO, stream=sys.stderr)")
                
        else:
            print("\n✅ All checks passed! MCP should load successfully.")
            
        print("\n📋 NEXT STEPS")
        print("-" * 60)
        print("1. Fix any ❌ failures listed above")
        print("2. Re-run this diagnostic to verify fixes")
        print("3. Test in Claude Code with: claude mcp add <name> \"python3 server.py\"")
        print("4. If still failing, check Claude logs: ~/Library/Logs/Claude/")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python diagnose_mcp_failure.py <path_to_mcp>")
        print("Example: python diagnose_mcp_failure.py ./my-mcp-server")
        sys.exit(1)
        
    mcp_path = sys.argv[1]
    diagnostics = MCPDiagnostics(mcp_path)
    diagnostics.run_diagnostics()


if __name__ == "__main__":
    main()