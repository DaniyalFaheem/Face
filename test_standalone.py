"""
test_standalone.py - Comprehensive validation framework for standalone executable

This script validates that all components work correctly in the packaged
application. It tests imports, model loading, file operations, and more.

Usage:
    python test_standalone.py [--verbose]
    
Generates a validation_report.json file with test results.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path


class ValidationReport:
    """Manages validation test results."""
    
    def __init__(self):
        self.tests = []
        self.start_time = datetime.now()
        
    def add_test(self, name, passed, message='', duration=0):
        """Add a test result."""
        self.tests.append({
            'name': name,
            'passed': passed,
            'message': message,
            'duration': duration,
        })
        
    def get_summary(self):
        """Get test summary."""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t['passed'])
        failed = total - passed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'timestamp': self.start_time.isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds(),
        }
    
    def save(self, filename='validation_report.json'):
        """Save report to JSON file."""
        report = {
            'summary': self.get_summary(),
            'tests': self.tests,
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
    
    def print_summary(self):
        """Print test summary to console."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total tests:    {summary['total']}")
        print(f"Passed:         {summary['passed']} ✓")
        print(f"Failed:         {summary['failed']} ✗")
        print(f"Success rate:   {summary['success_rate']:.1f}%")
        print(f"Duration:       {summary['duration']:.2f} seconds")
        print("=" * 60)
        
        # Show failed tests
        failed = [t for t in self.tests if not t['passed']]
        if failed:
            print("\nFailed tests:")
            for test in failed:
                print(f"  ✗ {test['name']}")
                if test['message']:
                    print(f"    {test['message']}")


def test_imports(report, verbose=False):
    """Test that all required modules can be imported."""
    if verbose:
        print("\n--- Testing Imports ---")
    
    modules = [
        ('cv2', 'OpenCV'),
        ('pandas', 'Pandas'),
        ('PIL', 'Pillow'),
        ('numpy', 'NumPy'),
        ('deepface', 'DeepFace'),
        ('tensorflow', 'TensorFlow'),
        ('pywhatkit', 'PyWhatKit'),
        ('pyautogui', 'PyAutoGUI'),
    ]
    
    for module_name, display_name in modules:
        try:
            start = datetime.now()
            __import__(module_name)
            duration = (datetime.now() - start).total_seconds()
            
            report.add_test(
                f"Import {display_name}",
                True,
                f"Successfully imported {module_name}",
                duration
            )
            if verbose:
                print(f"  ✓ {display_name} ({duration:.2f}s)")
        except ImportError as e:
            report.add_test(
                f"Import {display_name}",
                False,
                f"Failed to import {module_name}: {e}"
            )
            if verbose:
                print(f"  ✗ {display_name}: {e}")


def test_environment(report, verbose=False):
    """Test environment configuration."""
    if verbose:
        print("\n--- Testing Environment ---")
    
    # Check if running as frozen
    is_frozen = getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS') or '__compiled__' in globals()
    
    report.add_test(
        "Detect execution mode",
        True,
        f"Running as {'frozen' if is_frozen else 'script'}"
    )
    if verbose:
        print(f"  Execution mode: {'frozen' if is_frozen else 'script'}")
    
    # Check environment variables
    env_vars = ['TF_CPP_MIN_LOG_LEVEL', 'DEEPFACE_HOME']
    for var in env_vars:
        value = os.getenv(var)
        report.add_test(
            f"Environment variable {var}",
            value is not None,
            f"{var}={value}" if value else f"{var} not set"
        )
        if verbose:
            print(f"  {var}: {value if value else 'not set'}")


def test_resource_manager(report, verbose=False):
    """Test resource manager functionality."""
    if verbose:
        print("\n--- Testing Resource Manager ---")
    
    try:
        from resource_manager import get_resource_manager
        
        rm = get_resource_manager()
        
        # Test initialization
        report.add_test(
            "ResourceManager initialization",
            True,
            "ResourceManager created successfully"
        )
        
        # Test path resolution
        paths = {
            'bundle_dir': rm.get_bundle_dir(),
            'writable_dir': rm.get_writable_dir(),
        }
        
        for path_name, path_value in paths.items():
            exists = path_value.exists() if hasattr(path_value, 'exists') else os.path.exists(path_value)
            report.add_test(
                f"Path: {path_name}",
                exists,
                f"{path_name} = {path_value}"
            )
            if verbose:
                print(f"  {path_name}: {path_value} {'✓' if exists else '✗'}")
        
    except Exception as e:
        report.add_test(
            "ResourceManager initialization",
            False,
            f"Failed: {e}"
        )
        if verbose:
            print(f"  ✗ ResourceManager failed: {e}")


def test_opencv_cascade(report, verbose=False):
    """Test OpenCV cascade file loading."""
    if verbose:
        print("\n--- Testing OpenCV Cascade ---")
    
    try:
        import cv2
        from resource_manager import get_resource_manager
        
        rm = get_resource_manager()
        cascade_path = rm.get_opencv_cascade_path('haarcascade_frontalface_alt2.xml')
        
        # Check if file exists
        exists = os.path.exists(cascade_path)
        report.add_test(
            "Cascade file exists",
            exists,
            f"Path: {cascade_path}"
        )
        
        if exists:
            # Try to load cascade
            try:
                cascade = cv2.CascadeClassifier(cascade_path)
                is_empty = cascade.empty()
                
                report.add_test(
                    "Load cascade classifier",
                    not is_empty,
                    "Cascade loaded successfully" if not is_empty else "Cascade is empty"
                )
                if verbose:
                    print(f"  Cascade loaded: {'✓' if not is_empty else '✗'}")
            except Exception as e:
                report.add_test(
                    "Load cascade classifier",
                    False,
                    f"Failed to load: {e}"
                )
                if verbose:
                    print(f"  ✗ Failed to load cascade: {e}")
        else:
            if verbose:
                print(f"  ✗ Cascade file not found: {cascade_path}")
    
    except Exception as e:
        report.add_test(
            "OpenCV cascade test",
            False,
            f"Test failed: {e}"
        )
        if verbose:
            print(f"  ✗ Test failed: {e}")


def test_deepface_models(report, verbose=False):
    """Test DeepFace model loading."""
    if verbose:
        print("\n--- Testing DeepFace Models ---")
    
    try:
        import numpy as np
        from deepface import DeepFace
        
        # Create a test image
        test_img = np.zeros((224, 224, 3), dtype=np.uint8)
        
        # Test VGG-Face model
        try:
            start = datetime.now()
            result = DeepFace.find(
                img_path=test_img,
                db_path='.',
                model_name='VGG-Face',
                detector_backend='opencv',
                enforce_detection=False,
                silent=True
            )
            duration = (datetime.now() - start).total_seconds()
            
            report.add_test(
                "Load VGG-Face model",
                True,
                f"Model loaded in {duration:.2f}s",
                duration
            )
            if verbose:
                print(f"  ✓ VGG-Face model loaded ({duration:.2f}s)")
        except Exception as e:
            report.add_test(
                "Load VGG-Face model",
                False,
                f"Failed: {e}"
            )
            if verbose:
                print(f"  ✗ VGG-Face model failed: {e}")
        
        # Test SSD detector
        try:
            start = datetime.now()
            result = DeepFace.find(
                img_path=test_img,
                db_path='.',
                model_name='VGG-Face',
                detector_backend='ssd',
                enforce_detection=False,
                silent=True
            )
            duration = (datetime.now() - start).total_seconds()
            
            report.add_test(
                "Load SSD detector",
                True,
                f"Detector loaded in {duration:.2f}s",
                duration
            )
            if verbose:
                print(f"  ✓ SSD detector loaded ({duration:.2f}s)")
        except Exception as e:
            report.add_test(
                "Load SSD detector",
                False,
                f"Failed: {e}"
            )
            if verbose:
                print(f"  ✗ SSD detector failed: {e}")
    
    except Exception as e:
        report.add_test(
            "DeepFace model test",
            False,
            f"Test failed: {e}"
        )
        if verbose:
            print(f"  ✗ Test failed: {e}")


def test_file_operations(report, verbose=False):
    """Test file I/O operations."""
    if verbose:
        print("\n--- Testing File Operations ---")
    
    try:
        from resource_manager import get_resource_manager
        import pandas as pd
        
        rm = get_resource_manager()
        
        # Test writable directory
        test_file = rm.get_writable_path('test_write.txt')
        
        # Write test
        try:
            with open(test_file, 'w') as f:
                f.write("Test write operation")
            
            report.add_test(
                "File write operation",
                True,
                f"Successfully wrote to {test_file}"
            )
            if verbose:
                print(f"  ✓ Write test passed")
        except Exception as e:
            report.add_test(
                "File write operation",
                False,
                f"Failed: {e}"
            )
            if verbose:
                print(f"  ✗ Write test failed: {e}")
        
        # Read test
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            report.add_test(
                "File read operation",
                content == "Test write operation",
                "Successfully read file"
            )
            if verbose:
                print(f"  ✓ Read test passed")
        except Exception as e:
            report.add_test(
                "File read operation",
                False,
                f"Failed: {e}"
            )
            if verbose:
                print(f"  ✗ Read test failed: {e}")
        
        # CSV test
        try:
            csv_file = rm.get_writable_path('test_data.csv')
            df = pd.DataFrame({
                'Name': ['Test User'],
                'Date': ['2024-01-01'],
                'Time': ['12:00:00']
            })
            df.to_csv(csv_file, index=False)
            
            df_read = pd.read_csv(csv_file)
            
            report.add_test(
                "CSV operations",
                len(df_read) == 1,
                "Successfully created and read CSV"
            )
            if verbose:
                print(f"  ✓ CSV test passed")
            
            # Cleanup
            os.remove(csv_file)
        except Exception as e:
            report.add_test(
                "CSV operations",
                False,
                f"Failed: {e}"
            )
            if verbose:
                print(f"  ✗ CSV test failed: {e}")
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
    
    except Exception as e:
        report.add_test(
            "File operations test",
            False,
            f"Test failed: {e}"
        )
        if verbose:
            print(f"  ✗ Test failed: {e}")


def test_camera_access(report, verbose=False):
    """Test camera access (if available)."""
    if verbose:
        print("\n--- Testing Camera Access ---")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            
            report.add_test(
                "Camera access",
                ret and frame is not None,
                "Camera accessible" if ret else "Camera opened but no frame"
            )
            if verbose:
                print(f"  {'✓' if ret else '⚠'} Camera test: {frame.shape if ret else 'no frame'}")
        else:
            report.add_test(
                "Camera access",
                False,
                "No camera available (this is OK for testing)"
            )
            if verbose:
                print("  ⚠ No camera available (this is normal in some environments)")
    
    except Exception as e:
        report.add_test(
            "Camera access",
            False,
            f"Camera test failed: {e}"
        )
        if verbose:
            print(f"  ⚠ Camera test failed: {e}")


def main():
    """Main validation function."""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    print("\n╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "STANDALONE VALIDATION TEST" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    
    report = ValidationReport()
    
    # Run all tests
    test_imports(report, verbose)
    test_environment(report, verbose)
    test_resource_manager(report, verbose)
    test_opencv_cascade(report, verbose)
    test_deepface_models(report, verbose)
    test_file_operations(report, verbose)
    test_camera_access(report, verbose)
    
    # Print summary
    report.print_summary()
    
    # Save report
    try:
        from resource_manager import get_resource_manager
        rm = get_resource_manager()
        report_file = rm.get_writable_path('validation_report.json')
    except:
        report_file = 'validation_report.json'
    
    saved_file = report.save(report_file)
    print(f"\n📄 Report saved to: {saved_file}")
    
    # Return exit code based on results
    summary = report.get_summary()
    return 0 if summary['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
