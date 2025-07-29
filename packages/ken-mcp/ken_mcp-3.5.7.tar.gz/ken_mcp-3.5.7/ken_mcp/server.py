"""
KEN-MCP Server Entry Point
This file provides the main entry point for the KEN-MCP server package.
"""

import sys
import platform


def check_dependencies():
    """Check if all dependencies are properly installed"""
    try:
        # First, try to import basic dependencies
        import pydantic
        import httpx
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 Install ken-mcp with all dependencies:")
        print("   pip install ken-mcp")
        return False
        
    try:
        # Try to import fastmcp (this often fails due to cryptography issues)
        import fastmcp
    except ImportError as e:
        if "_cffi_backend" in str(e) or "cryptography" in str(e):
            print("❌ CFFI/Cryptography backend not properly installed.")
            print(f"\n💡 Detected OS: {platform.system()}")
            
            if platform.system() == "Linux":
                print("\n1. Install system dependencies:")
                print("   Ubuntu/Debian: sudo apt-get install python3-dev libffi-dev libssl-dev")
                print("   Fedora/RHEL:   sudo dnf install python3-devel libffi-devel openssl-devel")
                print("   Arch Linux:    sudo pacman -S python libffi openssl base-devel")
                print("\n2. Reinstall Python packages:")
                print("   pip install --upgrade --force-reinstall cffi cryptography")
                print("   pip install --upgrade ken-mcp")
            elif platform.system() == "Darwin":  # macOS
                print("\n1. Install Xcode Command Line Tools (if not already installed):")
                print("   xcode-select --install")
                print("\n2. If using Homebrew Python:")
                print("   brew install libffi openssl")
                print("   export LDFLAGS='-L/usr/local/opt/openssl/lib'")
                print("   export CPPFLAGS='-I/usr/local/opt/openssl/include'")
                print("\n3. Reinstall Python packages:")
                print("   pip install --upgrade --force-reinstall cffi cryptography")
                print("   pip install --upgrade ken-mcp")
            elif platform.system() == "Windows":
                print("\n1. Install Visual C++ Build Tools:")
                print("   Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
                print("   Or install Visual Studio Community with C++ support")
                print("\n2. Alternatively, use pre-compiled wheels:")
                print("   python -m pip install --upgrade pip")
                print("   pip install --only-binary :all: cffi cryptography")
                print("   pip install --upgrade ken-mcp")
                print("\n3. If still failing, try Anaconda/Miniconda:")
                print("   conda install cffi cryptography")
            else:
                print("\nReinstall the cryptography package:")
                print("   pip install --upgrade --force-reinstall cffi cryptography")
        elif "No module named 'typing_extensions'" in str(e):
            print("❌ Missing typing_extensions (required for older Python versions)")
            print("\n💡 Install it:")
            print("   pip install typing-extensions")
        elif "No module named 'authlib'" in str(e):
            print("❌ Missing authlib (required by fastmcp)")
            print("\n💡 Install it:")
            print("   pip install authlib")
        elif "DLL load failed" in str(e) and platform.system() == "Windows":
            print("❌ DLL load failed - this usually means missing Visual C++ redistributables")
            print("\n💡 Try:")
            print("   1. Install Visual C++ Redistributable:")
            print("      https://aka.ms/vs/17/release/vc_redist.x64.exe")
            print("   2. Or use Anaconda Python which includes these libraries")
        elif "Symbol not found" in str(e) and platform.system() == "Darwin":
            print("❌ Symbol not found - this usually means library version mismatch")
            print("\n💡 Try:")
            print("   1. Reinstall in a clean virtual environment:")
            print("      python3 -m venv fresh_env")
            print("      source fresh_env/bin/activate")
            print("      pip install ken-mcp")
            print("   2. Or use Homebrew Python instead of system Python")
        else:
            print(f"❌ Failed to import fastmcp: {e}")
            print("\n💡 Try:")
            print("   1. Reinstall in a virtual environment:")
            print("      python3 -m venv ken_env")
            print("      source ken_env/bin/activate  # or ken_env\\Scripts\\activate on Windows")
            print("      pip install --upgrade pip")
            print("      pip install ken-mcp")
            print("   2. Or check for specific error:")
            print("      python -c \"import fastmcp\" ")
        return False
        
    return True


def main():
    """Main entry point for ken-mcp-server command"""
    # Check dependencies before trying to import
    if not check_dependencies():
        sys.exit(1)
        
    try:
        # Import the mcp instance from generator module
        from ken_mcp.generator import mcp
        
        # Run the FastMCP server
        mcp.run()
    except Exception as e:
        print(f"\n❌ Error starting ken-mcp server: {e}")
        
        # Run detailed diagnostics
        print("\n🔍 Running diagnostics...")
        try:
            from ken_mcp.install_checker import check_installation
            check_installation()
        except:
            print("   Diagnostic tool not available")
            
        sys.exit(1)


if __name__ == "__main__":
    main()