"""
KEN-MCP Module Entry Point
Allows running the package as: python -m ken_mcp
"""

if __name__ == "__main__":
    try:
        from .server import main
        main()
    except ImportError as e:
        import sys
        import platform
        
        error_str = str(e)
        
        print(f"❌ Import error: {error_str}")
        
        if "fastmcp" in error_str:
            print("\n💡 FastMCP is not installed. Install ken-mcp with:")
            print("   pip install ken-mcp")
            print("\nIf you already installed it, you might be using a different Python.")
            print(f"Current Python: {sys.executable}")
        elif "_cffi_backend" in error_str:
            print("\n💡 CFFI backend issue detected.")
            if platform.system() == "Linux":
                print("\nFor Linux, install system dependencies first:")
                print("   Ubuntu/Debian: sudo apt-get install python3-dev libffi-dev libssl-dev")
                print("   Fedora/RHEL:   sudo dnf install python3-devel libffi-devel openssl-devel")
            print("\nThen reinstall:")
            print("   pip install --upgrade --force-reinstall cffi cryptography")
            print("   pip install --upgrade ken-mcp")
        else:
            print("\n💡 Try installing in a virtual environment:")
            print("   python3 -m venv ken_env")
            print("   source ken_env/bin/activate  # or ken_env\\Scripts\\activate on Windows")
            print("   pip install ken-mcp")
        
        sys.exit(1)
    except Exception as e:
        import sys
        print(f"❌ Error: {e}")
        sys.exit(1)