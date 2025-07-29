# KEN-MCP v3.4.0 Release Notes

## 🎉 Major Improvement: No More pip Pollution!

### What's Changed

Generated MCP servers no longer clutter your `pip list`! We've switched from making MCPs installable packages to simple dependency management.

### Key Changes:

1. **`requirements.txt` instead of `pyproject.toml`**
   - MCPs are no longer installed as packages
   - Just install dependencies: `pip install -r requirements.txt`
   - Your pip list stays clean!

2. **Simpler Installation**
   ```bash
   # Old way (v3.3.0 and earlier):
   pip install -e .  # This added the MCP to pip list!
   
   # New way (v3.4.0):
   pip install -r requirements.txt  # Only installs dependencies!
   ```

3. **No More Naming Conflicts**
   - Previously: Every MCP showed up in `pip list`
   - Now: Only actual dependencies are installed
   - Multiple MCPs can coexist without package conflicts

### Updated Features:

- All documentation updated to use `pip install -r requirements.txt`
- Diagnostic script (`diagnose.py`) checks for `requirements.txt`
- Help files reflect the new, cleaner approach
- Test suite validates the new structure

### File Structure:

Generated MCPs now include:
```
my-mcp/
├── server.py           # The MCP server
├── requirements.txt    # Dependencies only (NEW!)
├── diagnose.py         # Diagnostic script
├── test.py            # Test suite
├── help.md            # Setup guide
├── README.md          # Basic readme
├── .gitignore
├── .env.example
└── __init__.py
```

Note: `pyproject.toml` is no longer generated!

### Upgrading:

```bash
pip install --upgrade ken-mcp==3.4.0
```

### Benefits:

- ✅ Cleaner Python environment
- ✅ No package pollution in `pip list`
- ✅ Easier dependency management
- ✅ No naming conflicts between MCPs
- ✅ Simpler mental model - MCPs are scripts, not packages

View on PyPI: https://pypi.org/project/ken-mcp/3.4.0/