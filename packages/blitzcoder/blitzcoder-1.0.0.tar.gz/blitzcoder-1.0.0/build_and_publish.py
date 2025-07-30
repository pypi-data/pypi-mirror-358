#!/usr/bin/env python3
"""
Build and Publish Script for BlitzCoder

This script helps build and publish the BlitzCoder package to PyPI.
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}")

def build_package():
    """Build the package"""
    return run_command("python -m build", "Building package")

def check_package():
    """Check the package for issues"""
    return run_command("python -m twine check dist/*", "Checking package")

def upload_to_testpypi():
    """Upload to TestPyPI"""
    return run_command("python -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI")

def upload_to_pypi():
    """Upload to PyPI"""
    return run_command("python -m twine upload dist/*", "Uploading to PyPI")

def main():
    print("🚀 BlitzCoder PyPI Publishing Script")
    print("=" * 50)
    
    # Check if required tools are installed
    try:
        import build
        import twine
    except ImportError:
        print("❌ Required packages not found. Installing...")
        run_command("pip install build twine", "Installing build tools")
    
    # Clean previous builds
    clean_build()
    
    # Build the package
    if not build_package():
        print("❌ Build failed. Exiting.")
        sys.exit(1)
    
    # Check the package
    if not check_package():
        print("❌ Package check failed. Exiting.")
        sys.exit(1)
    
    print("\n📦 Package built successfully!")
    print("\nChoose an option:")
    print("1. Upload to TestPyPI (recommended for testing)")
    print("2. Upload to PyPI (production)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔬 Uploading to TestPyPI...")
        if upload_to_testpypi():
            print("\n✅ Package uploaded to TestPyPI successfully!")
            print("🔗 You can test it with: pip install --index-url https://test.pypi.org/simple/ blitzcoder")
        else:
            print("❌ Upload to TestPyPI failed.")
    
    elif choice == "2":
        print("\n⚠️  WARNING: This will upload to the main PyPI repository!")
        confirm = input("Are you sure you want to continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            if upload_to_pypi():
                print("\n✅ Package uploaded to PyPI successfully!")
                print("🔗 You can install it with: pip install blitzcoder")
            else:
                print("❌ Upload to PyPI failed.")
        else:
            print("❌ Upload cancelled.")
    
    else:
        print("👋 Exiting without upload.")

if __name__ == "__main__":
    main() 