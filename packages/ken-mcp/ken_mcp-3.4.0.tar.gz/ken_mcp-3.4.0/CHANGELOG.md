# Changelog

## [3.4.0] - 2024-01-XX
### Changed
- **No more pip pollution!** Generated MCPs now use `requirements.txt` instead of `pyproject.toml`
- MCPs are no longer installed as packages (no more cluttering `pip list`)
- Updated all documentation to use `pip install -r requirements.txt`
- Simplified dependency management - just install what's needed

### Improved
- Cleaner Python environment - MCPs don't register as installed packages
- Easier dependency updates - just edit requirements.txt
- No more package naming conflicts

## [3.3.0] - 2024-01-XX
### Added
- **Automatic diagnostic script** (`diagnose.py`) included in every generated MCP project
- Comprehensive MCP failure diagnostics checking:
  - Python version compatibility
  - Dependency installation status
  - stdout/stderr separation for JSON-RPC protocol
  - Print statement detection (breaks MCP protocol)
  - Logging configuration validation
  - Import and syntax error detection
  - JSON-RPC compliance testing
- Updated documentation to prominently feature diagnostics
- Enhanced instructions in generated files pointing to diagnostics

### Changed
- `help.md` now shows diagnostics as the first troubleshooting step
- `test.py` header directs to diagnostics for import errors
- `server.py` header mentions diagnostics for MCP loading failures
- Quick fix checklist prioritizes running diagnostics

### Fixed
- Better guidance for troubleshooting MCP loading issues
- Clearer error resolution paths with specific recommendations

## [3.2.2] - 2024-01-XX
### Fixed
- Critical stdout pollution issue preventing MCP servers from loading in Claude
- All output now properly redirected to stderr to preserve stdout for JSON-RPC protocol
- Fixed test generation to use correct FastMCP API (tool.fn instead of tool.function)

## [3.2.1] - 2024-01-XX
### Fixed
- Import issues in generated test files
- FastMCP API usage corrections

## [3.2.0] - 2024-01-XX
### Added
- Initial modular architecture
- Comprehensive test generation
- Better error handling and validation

## [3.1.0] - 2024-01-XX
### Added
- FastMCP integration
- Basic MCP server generation from natural language requirements