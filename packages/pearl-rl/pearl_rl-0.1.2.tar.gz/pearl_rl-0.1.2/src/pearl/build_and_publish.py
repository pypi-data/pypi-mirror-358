#!/usr/bin/env python3
"""
Build and publish script for Pearl RL library.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning build artifacts...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")

def build_package():
    """Build the package."""
    print("Building package...")
    if not run_command("python -m build"):
        print("Build failed!")
        return False
    return True

def check_package():
    """Check the built package."""
    print("Checking package...")
    if not run_command("python -m twine check dist/*"):
        print("Package check failed!")
        return False
    return True

def upload_to_test_pypi():
    """Upload to TestPyPI."""
    print("Uploading to TestPyPI...")
    if not run_command("python -m twine upload --repository testpypi dist/*"):
        print("Upload to TestPyPI failed!")
        return False
    return True

def upload_to_pypi():
    """Upload to PyPI."""
    print("Uploading to PyPI...")
    if not run_command("python -m twine upload dist/*"):
        print("Upload to PyPI failed!")
        return False
    return True

def main():
    """Main function."""
    print("Pearl RL - Build and Publish Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("Error: setup.py not found. Please run this script from the pearl directory.")
        sys.exit(1)
    
    # Install required tools
    print("Installing required tools...")
    run_command("pip install --upgrade build twine")
    
    # Clean previous builds
    clean_build()
    
    # Build package
    if not build_package():
        sys.exit(1)
    
    # Check package
    if not check_package():
        sys.exit(1)
    
    # Ask user what to do next
    print("\nPackage built successfully!")
    print("What would you like to do next?")
    print("1. Upload to TestPyPI (recommended for testing)")
    print("2. Upload to PyPI (production)")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        if upload_to_test_pypi():
            print("Successfully uploaded to TestPyPI!")
            print("You can test installation with: pip install --index-url https://test.pypi.org/simple/ pearl-rl")
    elif choice == "2":
        confirm = input("Are you sure you want to upload to PyPI? This will make the package publicly available. (y/N): ")
        if confirm.lower() == 'y':
            if upload_to_pypi():
                print("Successfully uploaded to PyPI!")
                print("Your package is now available at: https://pypi.org/project/pearl-rl/")
        else:
            print("Upload cancelled.")
    else:
        print("Exiting without uploading.")

if __name__ == "__main__":
    main() 