#!/usr/bin/env python3
"""
Helper script to build and publish the mareana-dtrack-mcp-server package to PyPI.
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to build and publish the package."""
    print("📦 Building and Publishing mareana-dtrack-mcp-server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: pyproject.toml not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Clean previous builds
    if not run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning previous builds"):
        sys.exit(1)
    
    # Build the package
    if not run_command("python -m build", "Building package"):
        print("\n💡 Hint: Install build tools with: pip install build twine")
        sys.exit(1)
    
    # Check the built package
    if not run_command("python -m twine check dist/*", "Checking package"):
        sys.exit(1)
    
    print("\n🎯 Package built successfully!")
    print("📁 Files created in dist/ directory:")
    
    # List the created files
    try:
        for file in os.listdir("dist"):
            print(f"   - {file}")
    except OSError:
        pass
    
    print("\n" + "=" * 50)
    print("🚀 Ready to publish!")
    print("\nTo publish to PyPI:")
    print("  1. Test on TestPyPI first:")
    print("     python -m twine upload --repository testpypi dist/*")
    print("  2. If everything looks good, upload to PyPI:")
    print("     python -m twine upload dist/*")
    print("\n💡 Make sure you have your PyPI credentials configured!")
    print("   You can use: python -m twine configure")

if __name__ == "__main__":
    main() 