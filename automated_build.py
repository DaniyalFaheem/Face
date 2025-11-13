"""
automated_build.py - Fully automated build script with dependency checking and error handling

This script performs a complete automated build with all checks and preparations.
It's designed to be run on Windows and will:
1. Check Python version
2. Install all dependencies
3. Download AI models
4. Copy required resources
5. Build with Nuitka
6. Create distributable package
7. Run validation tests

Usage:
    python automated_build.py

This is a one-command solution for creating the executable.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


class AutomatedBuilder:
    """Fully automated build manager with comprehensive error handling."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def print_header(self, text, char='='):
        """Print formatted header."""
        width = 80
        print("\n" + char * width)
        print(text.center(width))
        print(char * width + "\n")
    
    def print_step(self, step_num, total_steps, description):
        """Print step information."""
        print(f"\n{'='*80}")
        print(f"STEP {step_num}/{total_steps}: {description}")
        print('='*80 + "\n")
    
    def run_command(self, cmd, description=None, critical=True):
        """Run a command with error handling."""
        if description:
            print(f"→ {description}")
        
        print(f"$ {' '.join(cmd) if isinstance(cmd, list) else cmd}\n")
        
        try:
            result = subprocess.run(
                cmd,
                shell=isinstance(cmd, str),
                capture_output=True,
                text=True,
                check=False
            )
            
            # Show output
            if result.stdout:
                print(result.stdout)
            
            if result.returncode != 0:
                error_msg = f"Command failed with exit code {result.returncode}"
                if result.stderr:
                    error_msg += f"\n{result.stderr}"
                
                if critical:
                    self.errors.append(error_msg)
                    print(f"\n❌ ERROR: {error_msg}\n")
                    return False
                else:
                    self.warnings.append(error_msg)
                    print(f"\n⚠ WARNING: {error_msg}\n")
                    return True
            
            print("✓ Success\n")
            return True
            
        except Exception as e:
            error_msg = f"Exception running command: {e}"
            if critical:
                self.errors.append(error_msg)
                print(f"\n❌ ERROR: {error_msg}\n")
                return False
            else:
                self.warnings.append(error_msg)
                print(f"\n⚠ WARNING: {error_msg}\n")
                return True
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        self.print_step(1, 10, "Checking Python Version")
        
        version = sys.version_info
        print(f"Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major == 3 and version.minor == 8:
            print("✓ Python 3.8.x detected (optimal for TensorFlow)")
            return True
        elif version.major == 3 and 8 <= version.minor <= 12:
            print(f"⚠ Python 3.{version.minor} detected")
            print("  Python 3.8 is recommended for best compatibility")
            print("  Continuing anyway...")
            return True
        else:
            error = f"Python {version.major}.{version.minor} is not supported"
            self.errors.append(error)
            print(f"❌ {error}")
            print("  Please install Python 3.8-3.12")
            return False
    
    def install_dependencies(self):
        """Install all required dependencies."""
        self.print_step(2, 10, "Installing Dependencies")
        
        print("Installing from requirements-build.txt...")
        print("This may take 5-10 minutes...\n")
        
        # Upgrade pip first
        self.run_command(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            "Upgrading pip",
            critical=False
        )
        
        # Install requirements
        if not self.run_command(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements-build.txt'],
            "Installing all dependencies"
        ):
            return False
        
        # Install tf-keras if needed (for TensorFlow 2.20+)
        print("\nInstalling tf-keras (required for newer TensorFlow)...")
        self.run_command(
            [sys.executable, '-m', 'pip', 'install', 'tf-keras'],
            "Installing tf-keras",
            critical=False
        )
        
        print("\n✓ All dependencies installed")
        return True
    
    def verify_imports(self):
        """Verify all critical imports work."""
        self.print_step(3, 10, "Verifying Imports")
        
        required_modules = [
            ('cv2', 'OpenCV'),
            ('pandas', 'Pandas'),
            ('PIL', 'Pillow'),
            ('numpy', 'NumPy'),
            ('deepface', 'DeepFace'),
            ('tensorflow', 'TensorFlow'),
        ]
        
        all_ok = True
        for module_name, display_name in required_modules:
            try:
                __import__(module_name)
                print(f"  ✓ {display_name}")
            except ImportError as e:
                print(f"  ✗ {display_name}: {e}")
                self.errors.append(f"Failed to import {display_name}")
                all_ok = False
        
        if all_ok:
            print("\n✓ All imports verified")
        return all_ok
    
    def copy_opencv_cascade(self):
        """Copy OpenCV cascade file to project."""
        self.print_step(4, 10, "Preparing OpenCV Cascade")
        
        return self.run_command(
            [sys.executable, 'copy_opencv_cascade.py'],
            "Copying cascade file from OpenCV installation"
        )
    
    def prepare_models(self):
        """Download and prepare AI models."""
        self.print_step(5, 10, "Preparing AI Models")
        
        print("This will download ~500MB of AI models...")
        print("Estimated time: 5-10 minutes depending on internet speed\n")
        
        return self.run_command(
            [sys.executable, 'prepare_models.py'],
            "Downloading and preparing models"
        )
    
    def verify_models(self):
        """Verify models are ready."""
        self.print_step(6, 10, "Verifying Models")
        
        models_dir = self.project_root / 'deepface_models'
        marker_file = models_dir / 'MODELS_READY.txt'
        
        if marker_file.exists():
            print(f"✓ Models directory: {models_dir}")
            print(f"✓ Marker file: {marker_file}")
            
            with open(marker_file, 'r') as f:
                print(f"\nModel info:")
                print(f.read())
            return True
        else:
            self.errors.append("Models not prepared properly")
            print(f"❌ Models not found in {models_dir}")
            return False
    
    def clean_build_dirs(self):
        """Clean previous build artifacts."""
        self.print_step(7, 10, "Cleaning Build Directories")
        
        dirs_to_clean = ['dist', 'build']
        
        for dir_name in dirs_to_clean:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"  Removing {dir_path}")
                shutil.rmtree(dir_path)
        
        print("\n✓ Build directories cleaned")
        return True
    
    def build_with_nuitka(self):
        """Build executable with Nuitka."""
        self.print_step(8, 10, "Building Executable with Nuitka")
        
        print("Building standalone executable...")
        print("This will take 10-20 minutes. Please be patient...\n")
        
        # Build command
        cmd = [
            sys.executable, '-m', 'nuitka',
            '--standalone',
            '--onefile',
            '--enable-plugin=tk-inter',
            '--enable-plugin=numpy',
            '--nofollow-import-to=matplotlib',
            '--nofollow-import-to=IPython',
            f'--include-data-dir=deepface_models=deepface_models',
            f'--include-data-file=haarcascade_frontalface_alt2.xml=haarcascade_frontalface_alt2.xml',
        ]
        
        # Add icon if exists
        icon_file = self.project_root / 'icon.ico'
        if icon_file.exists():
            cmd.append(f'--windows-icon-from-ico={icon_file}')
        
        # Add optional resources
        for resource in ['send_button.png', 'background.jpg']:
            resource_file = self.project_root / resource
            if resource_file.exists():
                cmd.append(f'--include-data-file={resource}={resource}')
        
        # Windows specific options
        if sys.platform == 'win32':
            cmd.append('--windows-disable-console')
        
        # Output directory
        cmd.extend(['--output-dir=dist', 'app_launcher.py'])
        
        return self.run_command(cmd, "Compiling with Nuitka")
    
    def create_package(self):
        """Create distribution package."""
        self.print_step(9, 10, "Creating Distribution Package")
        
        # Use the build.py package creation logic
        return self.run_command(
            [sys.executable, 'build.py', '--skip-models', '--skip-tests'],
            "Creating package structure"
        )
    
    def run_tests(self):
        """Run validation tests."""
        self.print_step(10, 10, "Running Validation Tests")
        
        print("Running comprehensive validation...\n")
        
        # Run tests (don't fail if tests have issues)
        self.run_command(
            [sys.executable, 'test_standalone.py', '--verbose'],
            "Running validation suite",
            critical=False
        )
        
        return True
    
    def print_summary(self):
        """Print build summary."""
        self.print_header("BUILD SUMMARY", '=')
        
        if self.errors:
            print("❌ BUILD FAILED\n")
            print("Errors encountered:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
        else:
            print("✓ BUILD SUCCESSFUL!\n")
            
            if self.warnings:
                print("Warnings:")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
                print()
            
            # Show output location
            output_dir = self.project_root / 'dist' / 'FaceAttendanceSystem_Package'
            if output_dir.exists():
                exe_path = output_dir / 'FaceAttendanceSystem.exe'
                print(f"Executable ready: {exe_path}")
                print(f"Package ready: {output_dir}")
                
                # Show package contents
                print("\nPackage contents:")
                for item in sorted(output_dir.rglob('*')):
                    if item.is_file():
                        size_mb = item.stat().st_size / 1024 / 1024
                        rel_path = item.relative_to(output_dir)
                        print(f"  {rel_path} ({size_mb:.1f} MB)")
                
                # Calculate total size
                total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
                print(f"\nTotal package size: {total_size / 1024 / 1024:.1f} MB")
                
                print("\n" + "="*80)
                print("NEXT STEPS:")
                print("="*80)
                print("1. Test the executable:")
                print(f"   cd {output_dir}")
                print("   FaceAttendanceSystem.exe")
                print("\n2. The application will:")
                print("   - Start automatically (10-15 seconds first time)")
                print("   - Load AI models")
                print("   - Show login screen")
                print("   - Default credentials: admin/admin123 or user/user123")
                print("\n3. Distribute:")
                print("   - ZIP the FaceAttendanceSystem_Package folder")
                print("   - Share with users")
                print("   - Users just extract and run the .exe")
            
            return True
    
    def build(self):
        """Execute full automated build process."""
        self.print_header("AUTOMATED BUILD - FACE RECOGNITION ATTENDANCE SYSTEM")
        
        print("This script will:")
        print("  1. Check Python version")
        print("  2. Install all dependencies")
        print("  3. Verify imports")
        print("  4. Copy OpenCV cascade")
        print("  5. Download AI models (~500MB)")
        print("  6. Verify models")
        print("  7. Clean build directories")
        print("  8. Build executable with Nuitka (10-20 minutes)")
        print("  9. Create distribution package")
        print("  10. Run validation tests")
        print("\nTotal estimated time: 20-40 minutes")
        print("\nPress Ctrl+C to cancel, or Enter to continue...")
        
        try:
            input()
        except KeyboardInterrupt:
            print("\n\nBuild cancelled by user.")
            return False
        
        # Execute all steps
        steps = [
            self.check_python_version,
            self.install_dependencies,
            self.verify_imports,
            self.copy_opencv_cascade,
            self.prepare_models,
            self.verify_models,
            self.clean_build_dirs,
            self.build_with_nuitka,
            self.create_package,
            self.run_tests,
        ]
        
        for step_func in steps:
            if not step_func():
                print(f"\n❌ Build failed at: {step_func.__name__}")
                self.print_summary()
                return False
        
        return self.print_summary()


def main():
    """Main entry point."""
    builder = AutomatedBuilder()
    
    try:
        success = builder.build()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠ Build interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
