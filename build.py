"""
build.py - Complete automated build process for Face Recognition Attendance System

This script automates the entire build process using Nuitka to create a
standalone executable for Windows.

Usage:
    python build.py [options]
    
Options:
    --full          Full build with model preparation
    --skip-models   Skip model preparation (use existing)
    --skip-tests    Skip validation tests
    --clean         Clean build directories before building
    --onefile       Create single-file executable (default)
    --standalone    Create standalone directory (not single file)

Example:
    python build.py --full --clean
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


class BuildManager:
    """Manages the build process."""
    
    def __init__(self, args):
        self.args = args
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / 'dist'
        self.build_dir = self.project_root / 'build'
        self.output_dir = self.dist_dir / 'FaceAttendanceSystem_Package'
        
    def print_header(self, text):
        """Print a formatted header."""
        print("\n" + "=" * 80)
        print(text.center(80))
        print("=" * 80 + "\n")
    
    def step(self, number, total, description):
        """Print a step header."""
        print(f"\n[{number}/{total}] {description}")
        print("-" * 80)
    
    def run_command(self, cmd, description=None, check=True):
        """Run a command and handle errors."""
        if description:
            print(f"\n> {description}")
        print(f"$ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, check=check, 
                                       capture_output=False, text=True)
            else:
                result = subprocess.run(cmd, check=check, 
                                       capture_output=False, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Command failed with exit code {e.returncode}")
            return False
        except Exception as e:
            print(f"\n❌ Command failed: {e}")
            return False
    
    def clean_build_dirs(self):
        """Clean build and dist directories."""
        self.step(1, 8, "Cleaning build directories")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"  Removing {dir_path}")
                shutil.rmtree(dir_path)
                print(f"  ✓ Removed {dir_path}")
        
        print("\n✓ Build directories cleaned")
        return True
    
    def prepare_models(self):
        """Prepare DeepFace models."""
        self.step(2, 8, "Preparing DeepFace models")
        
        if self.args.skip_models:
            print("⚠ Skipping model preparation (--skip-models)")
            
            # Check if models exist
            models_dir = self.project_root / 'deepface_models'
            if models_dir.exists():
                print("✓ Using existing models")
                return True
            else:
                print("❌ No models found and --skip-models specified")
                return False
        
        # Run prepare_models.py
        return self.run_command(
            [sys.executable, 'prepare_models.py'],
            "Running model preparation script"
        )
    
    def install_dependencies(self):
        """Install build dependencies."""
        self.step(3, 8, "Installing build dependencies")
        
        # Check if requirements-build.txt exists
        req_file = self.project_root / 'requirements-build.txt'
        if not req_file.exists():
            print("⚠ requirements-build.txt not found, skipping")
            return True
        
        return self.run_command(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements-build.txt'],
            "Installing from requirements-build.txt"
        )
    
    def build_with_nuitka(self):
        """Build the application with Nuitka."""
        self.step(4, 8, "Building with Nuitka")
        
        # Nuitka command
        cmd = [
            sys.executable, '-m', 'nuitka',
            '--standalone',
            '--onefile' if self.args.onefile else '',
            '--enable-plugin=tk-inter',
            '--enable-plugin=numpy',
            '--nofollow-import-to=matplotlib',
            '--nofollow-import-to=IPython',
            '--include-data-dir=deepface_models=deepface_models',
            '--include-data-file=haarcascade_frontalface_alt2.xml=haarcascade_frontalface_alt2.xml',
            '--include-data-file=send_button.png=send_button.png',
            '--windows-disable-console',
            '--windows-icon-from-ico=icon.ico' if (self.project_root / 'icon.ico').exists() else '',
            '--output-dir=dist',
            'app_launcher.py'
        ]
        
        # Remove empty strings
        cmd = [c for c in cmd if c]
        
        print("Building executable (this may take 10-20 minutes)...")
        print("Command:", ' '.join(cmd))
        
        success = self.run_command(cmd, "Running Nuitka build")
        
        if success:
            print("\n✓ Nuitka build completed successfully")
        
        return success
    
    def create_package_structure(self):
        """Create the final package structure."""
        self.step(5, 8, "Creating package structure")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created: {self.output_dir}")
        
        # Find the executable
        if self.args.onefile:
            exe_name = 'app_launcher.exe'
            exe_src = self.dist_dir / exe_name
        else:
            exe_src = self.dist_dir / 'app_launcher.dist'
        
        if not exe_src.exists():
            print(f"❌ Executable not found: {exe_src}")
            return False
        
        # Copy executable
        exe_dest = self.output_dir / 'FaceAttendanceSystem.exe'
        if self.args.onefile:
            shutil.copy2(exe_src, exe_dest)
            print(f"  ✓ Copied executable: {exe_dest}")
        else:
            if exe_dest.exists():
                shutil.rmtree(exe_dest)
            shutil.copytree(exe_src, exe_dest)
            print(f"  ✓ Copied executable directory: {exe_dest}")
        
        # Create face_database directory
        db_dir = self.output_dir / 'face_database'
        db_dir.mkdir(exist_ok=True)
        print(f"  ✓ Created: {db_dir}")
        
        # Create README.txt
        readme_path = self.output_dir / 'README.txt'
        self.create_readme(readme_path)
        print(f"  ✓ Created: {readme_path}")
        
        # Copy LICENSE if exists
        license_src = self.project_root / 'LICENSE'
        if license_src.exists():
            license_dest = self.output_dir / 'LICENSE.txt'
            shutil.copy2(license_src, license_dest)
            print(f"  ✓ Copied: {license_dest}")
        
        # Copy additional resources if they exist
        resources = ['send_button.png', 'background.jpg']
        for resource in resources:
            resource_src = self.project_root / resource
            if resource_src.exists():
                resource_dest = self.output_dir / resource
                shutil.copy2(resource_src, resource_dest)
                print(f"  ✓ Copied: {resource}")
        
        print("\n✓ Package structure created")
        return True
    
    def create_readme(self, path):
        """Create README.txt file."""
        readme_content = f"""Face Recognition Attendance System
{'=' * 60}

Version: 1.0.0
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM REQUIREMENTS
-------------------
- Windows 10 or Windows 11
- Webcam (for face recognition)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

INSTALLATION
------------
1. Extract all files to a folder on your computer
2. Run FaceAttendanceSystem.exe
3. Default login credentials:
   - Admin: username=admin, password=admin123
   - User:  username=user,  password=user123

FIRST TIME SETUP
----------------
1. Launch the application
2. Login with admin credentials
3. Register users using the "Register New User" button
4. Follow the on-screen instructions to capture faces

FEATURES
--------
- Real-time face recognition
- Student and Faculty attendance tracking
- Automated WhatsApp notifications for absentees
- Salary calculation for faculty
- Attendance reports and logs

DATA LOCATION
-------------
All data (face database, attendance logs) is stored in:
Windows: C:\\Users\\<YourUsername>\\AppData\\Local\\FaceAttendanceSystem\\

TROUBLESHOOTING
---------------
1. If the application doesn't start:
   - Check Windows Event Viewer for errors
   - Run as Administrator
   - Disable antivirus temporarily

2. If camera doesn't work:
   - Check camera permissions in Windows Settings
   - Ensure no other application is using the camera

3. If face recognition is slow:
   - Close other applications
   - Ensure good lighting
   - Move closer to the camera

4. Display scaling issues:
   - Set Windows display scaling to 100%
   - Or set DPI awareness in app properties

SUPPORT
-------
For issues and questions, please visit:
https://github.com/DaniyalFaheem/Face

CREDITS
-------
- DeepFace: Face recognition framework
- OpenCV: Computer vision library
- TensorFlow: Machine learning framework

LICENSE
-------
See LICENSE.txt for terms and conditions.

{'=' * 60}
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def run_validation_tests(self):
        """Run validation tests."""
        self.step(6, 8, "Running validation tests")
        
        if self.args.skip_tests:
            print("⚠ Skipping validation tests (--skip-tests)")
            return True
        
        # Run test_standalone.py
        success = self.run_command(
            [sys.executable, 'test_standalone.py', '--verbose'],
            "Running standalone validation tests",
            check=False  # Don't fail build if tests fail
        )
        
        # Copy validation report to package
        report_src = Path('validation_report.json')
        if report_src.exists():
            report_dest = self.output_dir / 'validation_log.json'
            shutil.copy2(report_src, report_dest)
            print(f"  ✓ Copied validation report to package")
        
        return True  # Don't fail build on test failure
    
    def create_build_info(self):
        """Create build information file."""
        self.step(7, 8, "Creating build information")
        
        build_info = {
            'build_date': datetime.now().isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
            'onefile': self.args.onefile,
            'models_included': (self.project_root / 'deepface_models').exists(),
        }
        
        import json
        info_file = self.output_dir / 'build_info.json'
        with open(info_file, 'w') as f:
            json.dump(build_info, f, indent=2)
        
        print(f"  ✓ Created: {info_file}")
        print("\n✓ Build information created")
        return True
    
    def print_summary(self):
        """Print build summary."""
        self.step(8, 8, "Build Summary")
        
        print(f"Output directory: {self.output_dir}")
        print(f"\nPackage contents:")
        
        for item in sorted(self.output_dir.rglob('*')):
            if item.is_file():
                size = item.stat().st_size
                rel_path = item.relative_to(self.output_dir)
                print(f"  {rel_path} ({size / 1024 / 1024:.2f} MB)")
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in self.output_dir.rglob('*') if f.is_file())
        print(f"\nTotal package size: {total_size / 1024 / 1024:.2f} MB")
        
        print("\n" + "=" * 80)
        print("BUILD COMPLETED SUCCESSFULLY".center(80))
        print("=" * 80)
        print(f"\n✓ Executable ready: {self.output_dir / 'FaceAttendanceSystem.exe'}")
        print(f"✓ Package ready: {self.output_dir}")
        print("\nNext steps:")
        print("  1. Test the executable")
        print("  2. Create installer (optional)")
        print("  3. Distribute the package")
        
        return True
    
    def build(self):
        """Execute the full build process."""
        self.print_header("FACE RECOGNITION ATTENDANCE SYSTEM - BUILD PROCESS")
        
        print(f"Project root: {self.project_root}")
        print(f"Output directory: {self.output_dir}")
        print(f"Build type: {'Single file' if self.args.onefile else 'Standalone directory'}")
        
        steps = [
            (self.clean_build_dirs, self.args.clean),
            (self.prepare_models, True),
            (self.install_dependencies, True),
            (self.build_with_nuitka, True),
            (self.create_package_structure, True),
            (self.run_validation_tests, True),
            (self.create_build_info, True),
            (self.print_summary, True),
        ]
        
        for step_func, should_run in steps:
            if not should_run:
                continue
            
            if not step_func():
                print(f"\n❌ Build failed at step: {step_func.__name__}")
                return False
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build Face Recognition Attendance System executable'
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Full build with model preparation')
    parser.add_argument('--skip-models', action='store_true',
                       help='Skip model preparation (use existing)')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip validation tests')
    parser.add_argument('--clean', action='store_true',
                       help='Clean build directories before building')
    parser.add_argument('--onefile', action='store_true', default=True,
                       help='Create single-file executable (default)')
    parser.add_argument('--standalone', dest='onefile', action='store_false',
                       help='Create standalone directory (not single file)')
    
    args = parser.parse_args()
    
    # --full implies --clean
    if args.full:
        args.clean = True
    
    # Build
    builder = BuildManager(args)
    success = builder.build()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
