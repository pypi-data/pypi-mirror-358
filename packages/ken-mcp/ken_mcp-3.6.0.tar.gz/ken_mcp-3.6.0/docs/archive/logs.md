# Solutions - Todo MD MCP Development Issues and Fixes

## Overview
This document outlines the issues encountered during the development of the todo-md-mcp server and the solutions applied to resolve them.

## Initial Issues and Their Fixes

### 1. Generated Placeholder Code
**Issue**: The ken-mcp generator created a skeleton with placeholder functions that didn't implement the actual todo list functionality.

**Fix**: Completely rewrote `server.py` to implement:
- Proper todo list management functions
- Markdown parsing and formatting functions
- File I/O operations for .md files
- CRUD operations matching the requirements

### 2. Test Framework Incompatibility
**Issue**: The generated test file used incorrect methods to access MCP tools, resources, and prompts:
- Tried to access private attributes like `mcp._tools`, `mcp._resources`, `mcp._prompts`
- These attributes don't exist in the FastMCP framework

**Fix**: Updated test file to use public API methods:
- Changed from `mcp._tools.values()` to `await mcp.get_tool("tool_name")`
- Changed from `mcp._resources` to `await mcp.get_resources()`
- Changed from `mcp._prompts` to `await mcp.get_prompts()`

### 3. Async/Await Issues
**Issue**: Test code didn't properly await async methods:
- `mcp.get_tool()` returns a coroutine, not a direct result
- Led to "coroutine was never awaited" warnings

**Fix**: Added `await` keywords for all async method calls:
```python
# Before: tool_func = mcp.get_tool("create_todo_list")
# After:  tool = await mcp.get_tool("create_todo_list")
```

### 4. Tool Object Structure Misunderstanding
**Issue**: Assumed tool objects had a `.function` attribute, but they actually have a `.fn` attribute.

**Fix**: Changed all references from `tool.function` to `tool.fn`:
```python
# Before: tool_func = tool.function
# After:  tool_func = tool.fn
```

### 5. Resource and Prompt Return Types
**Issue**: Expected `get_resources()` and `get_prompts()` to return lists, but they return dictionaries.

**Fix**: Updated test logic to work with dictionaries:
```python
# Before: resources = await mcp.get_resources()
#         resource_names = [r.uri for r in resources]
# After:  resources = await mcp.get_resources()
#         assert "todo://lists" in resources  # dict key check
```

### 6. Environment Variable Timing
**Issue**: Test directory path was set via environment variable AFTER importing the server module, causing the server to use the default path instead of the test path.

**Fix**: Moved environment variable setup BEFORE importing the server:
```python
# Set up test environment BEFORE importing
os.environ["TODO_DIR"] = str(TEST_TODO_DIR)

# Import the generated server
from server import mcp
```

### 7. Tool Naming Mismatch
**Issue**: Test file looked for tools with generic names (create_todo, get_todo) while the implementation used specific names (create_todo_list, add_todo_item).

**Fix**: Updated all tool names in tests to match the actual implementation:
- `create_todo` → `create_todo_list`
- `get_todo` → `get_todo_list`
- `list_todos` → `list_todo_lists`
- etc.

### 8. Missing Tool Implementations
**Issue**: Initial code had 6 placeholder tools that didn't match the requirements.

**Fix**: Implemented 8 specific tools for todo list management:
- `create_todo_list` - Create new lists
- `add_todo_item` - Add items to lists
- `get_todo_list` - Read lists
- `list_todo_lists` - List all lists
- `update_todo_item` - Update items
- `delete_todo_item` - Delete items
- `delete_todo_list` - Delete lists
- `search_todos` - Search functionality

### 9. Resource Function Calls
**Issue**: Resource objects also use `.fn` attribute, not `.function`.

**Fix**: Updated resource function calls:
```python
# Before: result = await resource_obj.function()
# After:  result = await resource_obj.fn()
```

### 10. Prompt Function Calls
**Issue**: Similar to resources, prompt objects use `.fn` attribute.

**Fix**: Updated prompt function calls:
```python
# Before: result = prompt_obj.function()
# After:  result = prompt_obj.fn()
```

## Key Learnings

1. **FastMCP API**: Always use the public API methods (`get_tool`, `get_resources`, etc.) rather than trying to access internal attributes.

2. **Async Patterns**: FastMCP uses async/await extensively - ensure all MCP method calls are properly awaited.

3. **Object Attributes**: Tool, Resource, and Prompt objects expose their callable function via the `.fn` attribute, not `.function`.

4. **Return Types**: Check the actual return types of methods - `get_resources()` and `get_prompts()` return dictionaries, not lists.

5. **Environment Setup**: When testing, ensure environment variables are set before importing modules that use them.

6. **Test-Driven Development**: The comprehensive test suite helped identify all these issues systematically.

## Final Result

After addressing all issues:
- All 8 tests pass successfully
- The MCP server properly manages todo lists in markdown format
- Full CRUD operations work as expected
- The server is ready for integration with Claude Desktop