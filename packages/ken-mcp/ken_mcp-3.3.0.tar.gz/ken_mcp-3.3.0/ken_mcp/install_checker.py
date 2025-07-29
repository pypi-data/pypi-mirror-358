#!/usr/bin/env python3
"""
Installation checker for ken-mcp
Verifies all dependencies are properly installed and provides helpful error messages
"""

import sys
import platform
import subprocess
import importlib.util


class InstallChecker:
    """Check and diagnose installation issues"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.system = platform.system()
        self.python_version = sys.version_info
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        if self.python_version < (3, 8):
            self.errors.append(
                f"Python {self.python_version.major}.{self.python_version.minor} detected. "
                f"ken-mcp requires Python 3.8 or higher."
            )
            return False
        return True
    
    def check_import(self, module_name, package_name=None):
        """Check if a module can be imported"""
        if package_name is None:
            package_name = module_name
            
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        try:
            __import__(module_name)
            return True
        except ImportError as e:
            if "_cffi_backend" in str(e):
                self.errors.append(
                    f"CFFI backend not properly installed. This is a common issue on Linux.\n"
                    f"Please run:\n"
                    f"  Ubuntu/Debian: sudo apt-get install python3-dev libffi-dev libssl-dev\n"
                    f"  Fedora/RHEL:   sudo dnf install python3-devel libffi-devel openssl-devel\n"
                    f"  Then: pip install --upgrade --force-reinstall cffi cryptography"
                )
            else:
                self.errors.append(f"Failed to import {module_name}: {e}")
            return False
    
    def check_system_deps(self):
        """Check system dependencies based on OS"""
        if self.system == "Linux":
            # Check for common missing packages on Linux
            missing_hints = []
            
            # Try to detect which packages might be missing
            try:
                # Check for dev headers
                import sysconfig
                include_dir = sysconfig.get_paths()['include']
                python_h = f"{include_dir}/Python.h"
                
                import os
                if not os.path.exists(python_h):
                    missing_hints.append("python3-dev (or python3-devel)")
            except:
                pass
                
            if missing_hints:
                self.warnings.append(
                    f"Possible missing system packages: {', '.join(missing_hints)}\n"
                    f"Install with your package manager before proceeding."
                )
                
        elif self.system == "Darwin":  # macOS
            # Check for Xcode Command Line Tools
            try:
                result = subprocess.run(['xcode-select', '-p'], 
                                     capture_output=True, text=True)
                if result.returncode != 0:
                    self.warnings.append(
                        "Xcode Command Line Tools may not be installed.\n"
                        "Run: xcode-select --install"
                    )
            except:
                pass
                
        elif self.system == "Windows":
            # Check for Visual C++ compiler
            try:
                import distutils.msvccompiler
                if not distutils.msvccompiler.get_build_version():
                    self.warnings.append(
                        "Visual C++ compiler not found.\n"
                        "Install Visual Studio Build Tools or use pre-compiled wheels."
                    )
            except:
                # On newer Python versions, different check
                self.warnings.append(
                    "Consider using pre-compiled wheels:\n"
                    "pip install --only-binary :all: cffi cryptography"
                )
    
    def check_dependencies(self):
        """Check all Python dependencies"""
        deps = [
            ("fastmcp", "fastmcp"),
            ("httpx", "httpx"),
            ("pydantic", "pydantic"),
            ("cffi", "cffi"),
            ("cryptography", "cryptography"),
            ("typing_extensions", "typing-extensions"),  # Often missing on older Python
            ("authlib", "authlib"),  # Required by fastmcp
        ]
        
        all_ok = True
        for module, package in deps:
            if not self.check_import(module, package):
                all_ok = False
                
        return all_ok
    
    def check_network_connectivity(self):
        """Check if pip can reach PyPI"""
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org/', timeout=5)
            return True
        except Exception as e:
            self.warnings.append(
                "Cannot reach PyPI. If you're behind a proxy, configure it:\n"
                "  export HTTP_PROXY=http://your-proxy:port\n"
                "  export HTTPS_PROXY=http://your-proxy:port\n"
                "  pip config set global.proxy http://your-proxy:port"
            )
            return False
    
    def check_pip_version(self):
        """Check if pip is recent enough"""
        try:
            import subprocess
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Extract version from "pip X.Y.Z from ..."
                version_str = result.stdout.split()[1]
                major = int(version_str.split('.')[0])
                if major < 20:
                    self.warnings.append(
                        f"Your pip version ({version_str}) is outdated.\n"
                        f"Update with: {sys.executable} -m pip install --upgrade pip"
                    )
            else:
                self.errors.append("pip is not working properly")
        except:
            self.warnings.append("Could not check pip version")
    
    def check_permissions(self):
        """Check if user has write permissions"""
        import site
        user_site = site.getusersitepackages()
        
        try:
            # Check if we can write to user site-packages
            import os
            os.makedirs(user_site, exist_ok=True)
            test_file = os.path.join(user_site, '.ken_mcp_test')
            
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
        except PermissionError:
            self.warnings.append(
                "No write permission to install packages. Try:\n"
                f"  pip install --user ken-mcp\n"
                f"  or use a virtual environment"
            )
        except:
            pass
    
    def check_path_issues(self):
        """Check if scripts directory is in PATH"""
        import site
        import os
        
        # Get the scripts directory
        if self.system == "Windows":
            scripts_dir = os.path.join(site.USER_BASE, "Scripts")
        else:
            scripts_dir = os.path.join(site.USER_BASE, "bin")
            
        # Check if it's in PATH
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        if scripts_dir not in path_dirs and os.path.exists(scripts_dir):
            self.warnings.append(
                f"Scripts directory not in PATH. Add it:\n"
                f"  export PATH=\"{scripts_dir}:$PATH\"\n"
                f"  Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.)"
            )
    
    def get_install_command(self):
        """Get the appropriate install command for the system"""
        if self.system == "Linux":
            distro = ""
            try:
                with open("/etc/os-release") as f:
                    content = f.read().lower()
                    if "ubuntu" in content or "debian" in content:
                        distro = "debian"
                    elif "fedora" in content or "rhel" in content or "centos" in content:
                        distro = "redhat"
                    elif "arch" in content:
                        distro = "arch"
                    elif "alpine" in content:
                        distro = "alpine"
            except:
                pass
                
            if distro == "debian":
                return [
                    "sudo apt-get update && sudo apt-get install -y python3-dev libffi-dev libssl-dev build-essential",
                    "pip install --upgrade --force-reinstall cffi cryptography"
                ]
            elif distro == "redhat":
                return [
                    "sudo dnf install -y python3-devel libffi-devel openssl-devel gcc",
                    "pip install --upgrade --force-reinstall cffi cryptography"
                ]
            elif distro == "arch":
                return [
                    "sudo pacman -S python libffi openssl base-devel",
                    "pip install --upgrade --force-reinstall cffi cryptography"
                ]
            elif distro == "alpine":
                return [
                    "sudo apk add python3-dev libffi-dev openssl-dev musl-dev gcc",
                    "pip install --upgrade --force-reinstall cffi cryptography"
                ]
            else:
                return [
                    "Install python3-dev, libffi-dev, and libssl-dev using your package manager",
                    "pip install --upgrade --force-reinstall cffi cryptography"
                ]
        
        elif self.system == "Darwin":  # macOS
            return [
                "# Install Xcode Command Line Tools (if needed):",
                "xcode-select --install",
                "",
                "# If using Homebrew:",
                "brew install libffi openssl",
                "",
                "# Set environment variables and reinstall:",
                "export LDFLAGS='-L/usr/local/opt/openssl/lib'",
                "export CPPFLAGS='-I/usr/local/opt/openssl/include'", 
                "pip install --upgrade --force-reinstall cffi cryptography"
            ]
            
        elif self.system == "Windows":
            return [
                "# Option 1: Install Visual C++ Build Tools",
                "# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/",
                "",
                "# Option 2: Use pre-compiled wheels:",
                "python -m pip install --upgrade pip",
                "pip install --only-binary :all: cffi cryptography",
                "",
                "# Option 3: Use Anaconda/Miniconda:",
                "conda install cffi cryptography"
            ]
                
        return None
    
    def run_checks(self):
        """Run all installation checks"""
        print("🔍 Checking ken-mcp installation...\n")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check pip version
        self.check_pip_version()
        
        # Check network connectivity
        self.check_network_connectivity()
        
        # Check permissions
        self.check_permissions()
        
        # Check PATH issues
        self.check_path_issues()
            
        # Check system dependencies
        self.check_system_deps()
        
        # Check Python dependencies
        deps_ok = self.check_dependencies()
        
        # Show results
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   {warning}")
            print()
            
        if self.errors:
            print("❌ Errors found:")
            for error in self.errors:
                print(f"   {error}")
            print()
            
            # Provide system-specific help
            install_cmds = self.get_install_command()
            if install_cmds:
                print("💡 To fix system dependencies, run:")
                for cmd in install_cmds:
                    if cmd:  # Skip empty lines
                        print(f"   {cmd}")
                print()
                
            print("Then reinstall ken-mcp:")
            print("   pip install --upgrade ken-mcp")
            
            return False
            
        print("✅ All dependencies are properly installed!")
        return True


def check_installation():
    """Main function to check installation"""
    checker = InstallChecker()
    return checker.run_checks()


if __name__ == "__main__":
    success = check_installation()
    sys.exit(0 if success else 1)