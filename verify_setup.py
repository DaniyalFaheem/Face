"""
verify_setup.py - Quick verification script for development setup

This script performs basic checks to ensure the development environment
is properly configured before building.

Usage:
    python verify_setup.py
"""

import sys
import os


def check_python_version():
    """Check if Python version is 3.8.x."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 8:
        print("  ✓ Python 3.8.x detected (required for TensorFlow)")
        return True
    else:
        print(f"  ⚠ Warning: Python {version.major}.{version.minor} detected")
        print("  Recommended: Python 3.8.x for TensorFlow compatibility")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\nChecking dependencies:")
    
    dependencies = {
        'cv2': 'opencv-python',
        'pandas': 'pandas',
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'deepface': 'deepface',
        'tensorflow': 'tensorflow',
        'pywhatkit': 'pywhatkit',
        'pyautogui': 'pyautogui',
        'nuitka': 'nuitka',
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    return missing


def check_files():
    """Check if required project files exist."""
    print("\nChecking project files:")
    
    required_files = [
        'app.py',
        'app_launcher.py',
        'prepare_models.py',
        'resource_manager.py',
        'config.py',
        'build.py',
        'test_standalone.py',
        'requirements-build.txt',
        'BUILDING.md',
    ]
    
    missing = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} - MISSING")
            missing.append(filename)
    
    return missing


def check_opencv_cascade():
    """Check if OpenCV cascade file is available."""
    print("\nChecking OpenCV cascade file:")
    
    # Check if file exists in project
    if os.path.exists('haarcascade_frontalface_alt2.xml'):
        print("  ✓ haarcascade_frontalface_alt2.xml found in project")
        return True
    
    # Check if OpenCV is installed and has the cascade
    try:
        import cv2
        cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_alt2.xml')
        if os.path.exists(cascade_path):
            print(f"  ✓ Found in OpenCV: {cascade_path}")
            print("  ⚠ Run copy_opencv_cascade.py to copy to project")
            return True
    except (ImportError, AttributeError):
        pass
    
    print("  ✗ Cascade file not found")
    print("  → Install OpenCV and run: python copy_opencv_cascade.py")
    return False


def check_models():
    """Check if DeepFace models are prepared."""
    print("\nChecking AI models:")
    
    models_dir = 'deepface_models'
    
    if os.path.exists(models_dir):
        # Check for marker file
        marker = os.path.join(models_dir, 'MODELS_READY.txt')
        if os.path.exists(marker):
            print(f"  ✓ Models prepared in {models_dir}")
            with open(marker, 'r') as f:
                for line in f:
                    print(f"    {line.strip()}")
            return True
        else:
            print(f"  ⚠ {models_dir} exists but may be incomplete")
            return False
    else:
        print(f"  ✗ Models not prepared")
        print("  → Run: python prepare_models.py")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("  DEVELOPMENT ENVIRONMENT VERIFICATION")
    print("=" * 60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Files", check_files),
        ("OpenCV Cascade", check_opencv_cascade),
        ("AI Models", check_models),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        result = check_func()
        
        # Handle different return types
        if isinstance(result, bool):
            results[check_name] = result
        elif isinstance(result, list):
            results[check_name] = len(result) == 0
        else:
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60 + "\n")
    
    for check_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All checks passed! Ready to build.")
        print("\nNext steps:")
        print("  1. Run: python build.py --full")
        print("  2. Or: build.bat (Windows)")
        return 0
    else:
        print("\n⚠ Some checks failed. Please fix the issues above.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements-build.txt")
        print("\nTo prepare models:")
        print("  python prepare_models.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())
