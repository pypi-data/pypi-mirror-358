#!/usr/bin/env python3
"""
Build and publish script for mcp-cldkctl package
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['dist', 'build', '__pycache__']
    files_to_clean = ['*.egg-info']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            if file_path.is_dir():
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
            print(f"   Removed {file_path}")
    
    print("✅ Clean completed")

def run_tests():
    """Run package tests"""
    print("🧪 Running tests...")
    
    # Run the test script
    if run_command("python test_package.py", "Package tests"):
        print("✅ All tests passed")
        return True
    else:
        print("❌ Tests failed")
        return False

def build_package():
    """Build the package"""
    print("📦 Building package...")
    
    # Install build dependencies
    if not run_command("pip install build twine", "Installing build dependencies"):
        return False
    
    # Build the package
    if not run_command("python -m build", "Building package"):
        return False
    
    # Check the built package
    if not run_command("python -m twine check dist/*", "Checking package"):
        return False
    
    print("✅ Package built successfully")
    return True

def test_installation():
    """Test package installation"""
    print("🔍 Testing package installation...")
    
    # Test with uvx
    if run_command("uvx mcp-cldkctl --help", "Testing uvx installation"):
        print("✅ uvx installation test passed")
        return True
    else:
        print("❌ uvx installation test failed")
        return False

def publish_to_testpypi():
    """Publish to TestPyPI"""
    print("🚀 Publishing to TestPyPI...")
    
    if run_command("python -m twine upload --repository testpypi dist/*", "Publishing to TestPyPI"):
        print("✅ Published to TestPyPI successfully")
        print("🔗 TestPyPI URL: https://test.pypi.org/project/mcp-cldkctl/")
        return True
    else:
        print("❌ Failed to publish to TestPyPI")
        return False

def publish_to_pypi():
    """Publish to PyPI"""
    print("🚀 Publishing to PyPI...")
    
    if run_command("python -m twine upload dist/*", "Publishing to PyPI"):
        print("✅ Published to PyPI successfully")
        print("🔗 PyPI URL: https://pypi.org/project/mcp-cldkctl/")
        return True
    else:
        print("❌ Failed to publish to PyPI")
        return False

def main():
    """Main build and publish process"""
    print("🚀 Starting mcp-cldkctl build and publish process...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ pyproject.toml not found. Please run this script from the project root.")
        return 1
    
    # Read version from pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            if 'name = "mcp-cldkctl"' not in content:
                print("❌ Package name in pyproject.toml doesn't match expected 'mcp-cldkctl'")
                return 1
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return 1
    
    steps = [
        ("Clean build artifacts", clean_build),
        ("Run tests", run_tests),
        ("Build package", build_package),
        ("Test installation", test_installation),
    ]
    
    # Execute all steps
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 40)
        if not step_func():
            print(f"❌ Failed at step: {step_name}")
            return 1
    
    # Ask about publishing
    print("\n" + "=" * 60)
    print("📦 Package built successfully!")
    
    publish_choice = input("\nDo you want to publish? (testpypi/pypi/skip): ").lower().strip()
    
    if publish_choice == "testpypi":
        if not publish_to_testpypi():
            return 1
    elif publish_choice == "pypi":
        if not publish_to_testpypi():
            print("❌ TestPyPI publish failed, skipping PyPI")
            return 1
        if not publish_to_pypi():
            return 1
    elif publish_choice == "skip":
        print("⏭️  Skipping publish")
    else:
        print("❌ Invalid choice")
        return 1
    
    print("\n🎉 Build and publish process completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the published package: uvx mcp-cldkctl --help")
    print("2. Update documentation if needed")
    print("3. Create a GitHub release")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 