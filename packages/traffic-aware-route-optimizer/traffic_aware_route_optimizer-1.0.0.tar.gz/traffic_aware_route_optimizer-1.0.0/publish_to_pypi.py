#!/usr/bin/env python3
"""
PyPI Publishing Script for Traffic-Aware Route Optimizer
Automates the build, check, and upload process for PyPI.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n🔧 {description}...")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} successful!")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} failed!")
        if result.stderr:
            print(f"Error: {result.stderr}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return False
    return True

def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("\n🧹 Cleaning build artifacts...")
    
    artifacts = ['dist/', 'build/', '*.egg-info/']
    for pattern in artifacts:
        if pattern.endswith('/'):
            # Directory
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"   Removed {pattern}")
        else:
            # Glob pattern
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"   Removed {path}")

def check_dependencies():
    """Check if required tools are installed."""
    print("\n🔍 Checking dependencies...")
    
    required = ['build', 'twine']
    missing = []
    
    for tool in required:
        result = subprocess.run(f"python -m {tool} --help", 
                              shell=True, capture_output=True)
        if result.returncode != 0:
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("Install with: pip install build twine")
        return False
    
    print("✅ All dependencies available!")
    return True

def main():
    """Main publishing workflow."""
    print("🚀 Traffic-Aware Route Optimizer - PyPI Publishing Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('pyproject.toml'):
        print("❌ Error: pyproject.toml not found. Run this script from the package root.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean build artifacts
    clean_build_artifacts()
    
    # Build the package
    if not run_command("python -m build", "Building package"):
        sys.exit(1)
    
    # Check the package
    if not run_command("python -m twine check dist/*", "Checking package"):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Package build and check completed successfully!")
    print("\n📦 Built files:")
    if os.path.exists('dist'):
        for file in os.listdir('dist'):
            size = os.path.getsize(f'dist/{file}')
            print(f"   - {file} ({size:,} bytes)")
    
    print("\n🔄 Next steps:")
    print("1. Test upload to TestPyPI:")
    print("   python -m twine upload --repository testpypi dist/*")
    print("\n2. If test upload works, upload to PyPI:")
    print("   python -m twine upload dist/*")
    print("\n3. Test installation:")
    print("   pip install traffic-aware-route-optimizer")
    
    # Ask if user wants to continue with TestPyPI upload
    response = input("\n❓ Upload to TestPyPI now? (y/N): ")
    if response.lower() in ['y', 'yes']:
        if run_command("python -m twine upload --repository testpypi dist/*", 
                      "Uploading to TestPyPI"):
            print("\n✅ TestPyPI upload successful!")
            print("🧪 Test install with:")
            print("pip install --index-url https://test.pypi.org/simple/ traffic-aware-route-optimizer")
            
            # Ask about production upload
            response = input("\n❓ Upload to production PyPI? (y/N): ")
            if response.lower() in ['y', 'yes']:
                if run_command("python -m twine upload dist/*", 
                              "Uploading to PyPI"):
                    print("\n🎉 SUCCESS! Package published to PyPI!")
                    print("📦 Install with: pip install traffic-aware-route-optimizer")
                    print("🌐 View at: https://pypi.org/project/traffic-aware-route-optimizer/")

if __name__ == "__main__":
    main()
