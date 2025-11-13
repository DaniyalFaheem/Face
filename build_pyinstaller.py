"""
build_pyinstaller.py - Alternative build script using PyInstaller

This script provides an alternative to Nuitka using PyInstaller, which is:
- More cross-platform compatible
- Faster to build
- Works on Linux/Mac/Windows
- Compatible with Python 3.8-3.12

Usage:
    python build_pyinstaller.py [options]
    
Options:
    --full          Full build with model preparation
    --skip-models   Skip model preparation (use existing)
    --clean         Clean build directories before building
    --onedir        Create one-directory bundle (default)
    --onefile       Create one-file executable
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Configure stdout to use UTF-8 encoding to support Unicode characters
# This fixes encoding issues on Windows where default encoding is cp1252
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class PyInstallerBuilder:
    """Manages the build process using PyInstaller."""
    
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
        self.step(1, 7, "Cleaning build directories")
        
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
        self.step(2, 7, "Preparing DeepFace models")
        
        if self.args.skip_models:
            print("⚠ Skipping model preparation (--skip-models)")
            
            # Check if models exist
            models_dir = self.project_root / 'deepface_models'
            if models_dir.exists():
                print("✓ Using existing models")
                return True
            else:
                print("⚠ No models found but --skip-models specified")
                print("  Build will continue but may fail at runtime")
                return True
        
        # Run prepare_models.py
        return self.run_command(
            [sys.executable, 'prepare_models.py'],
            "Running model preparation script",
            check=False  # Don't fail if models can't be downloaded
        )
    
    def install_pyinstaller(self):
        """Install PyInstaller."""
        self.step(3, 7, "Installing PyInstaller")
        
        return self.run_command(
            [sys.executable, '-m', 'pip', 'install', 'pyinstaller', '--upgrade'],
            "Installing/upgrading PyInstaller"
        )
    
    def create_spec_file(self):
        """Create PyInstaller spec file."""
        self.step(4, 7, "Creating PyInstaller spec file")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# Project root
project_root = Path(SPECPATH)

# Data files to include
datas = []

# Add models directory if it exists
models_dir = project_root / 'deepface_models'
if models_dir.exists():
    datas.append(('deepface_models', 'deepface_models'))

# Add required data files
data_files = [
    'haarcascade_frontalface_alt2.xml',
    'send_button.png',
    'background.jpg',
]

for file in data_files:
    file_path = project_root / file
    if file_path.exists():
        datas.append((str(file_path), '.'))

# Hidden imports (packages that PyInstaller might miss)
hiddenimports = [
    'PIL._tkinter_finder',
    'pkg_resources.extern',
    'deepface',
    'deepface.basemodels',
    'deepface.extendedmodels',
    'deepface.commons',
    'tensorflow',
    'keras',
    'cv2',
    'retina_face',
]

a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FaceAttendanceSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FaceAttendanceSystem',
)
'''
        
        spec_file = self.project_root / 'FaceAttendanceSystem.spec'
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✓ Created spec file: {spec_file}")
        return True
    
    def build_with_pyinstaller(self):
        """Build the application with PyInstaller."""
        self.step(5, 7, "Building with PyInstaller")
        
        spec_file = self.project_root / 'FaceAttendanceSystem.spec'
        
        if not spec_file.exists():
            print("❌ Spec file not found")
            return False
        
        # PyInstaller command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(spec_file)
        ]
        
        print("Building executable (this may take 5-10 minutes)...")
        print("Command:", ' '.join(cmd))
        
        success = self.run_command(cmd, "Running PyInstaller build")
        
        if success:
            print("\n✓ PyInstaller build completed successfully")
        
        return success
    
    def create_package_structure(self):
        """Create the final package structure."""
        self.step(6, 7, "Creating package structure")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created: {self.output_dir}")
        
        # Find the built application
        built_dir = self.dist_dir / 'FaceAttendanceSystem'
        
        if not built_dir.exists():
            print(f"❌ Built application not found: {built_dir}")
            return False
        
        # Copy the entire built directory
        target_dir = self.output_dir / 'FaceAttendanceSystem'
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(built_dir, target_dir)
        print(f"  ✓ Copied application: {target_dir}")
        
        # Create face_database directory
        db_dir = self.output_dir / 'face_database'
        db_dir.mkdir(exist_ok=True)
        print(f"  ✓ Created: {db_dir}")
        
        # Create README.txt
        readme_path = self.output_dir / 'README.txt'
        self.create_readme(readme_path)
        print(f"  ✓ Created: {readme_path}")
        
        # Copy documentation files
        doc_files = ['QUICKSTART.txt', 'USER_GUIDE.md', 'LICENSE']
        for doc_file in doc_files:
            src = self.project_root / doc_file
            if src.exists():
                dest = self.output_dir / (doc_file if doc_file != 'LICENSE' else 'LICENSE.txt')
                shutil.copy2(src, dest)
                print(f"  ✓ Copied: {doc_file}")
        
        # Copy additional resources
        resources = ['send_button.png', 'background.jpg']
        for resource in resources:
            resource_src = self.project_root / resource
            if resource_src.exists():
                resource_dest = self.output_dir / resource
                shutil.copy2(resource_src, resource_dest)
                print(f"  ✓ Copied: {resource}")
        
        # Create run script for easy execution
        if sys.platform == 'win32':
            run_script = self.output_dir / 'Run_FaceAttendanceSystem.bat'
            with open(run_script, 'w') as f:
                f.write('@echo off\n')
                f.write('cd /d "%~dp0"\n')
                f.write('start "" "FaceAttendanceSystem\\FaceAttendanceSystem.exe"\n')
            print(f"  ✓ Created: {run_script}")
        else:
            run_script = self.output_dir / 'run_faceattendance.sh'
            with open(run_script, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write('cd "$(dirname "$0")"\n')
                f.write('./FaceAttendanceSystem/FaceAttendanceSystem\n')
            os.chmod(run_script, 0o755)
            print(f"  ✓ Created: {run_script}")
        
        print("\n✓ Package structure created")
        return True
    
    def create_readme(self, path):
        """Create README.txt file."""
        readme_content = f"""Face Recognition Attendance System
{'=' * 60}

Version: 1.0.0
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Build Method: PyInstaller

SYSTEM REQUIREMENTS
-------------------
- Windows 10 or Windows 11 (or Linux/macOS)
- Webcam (for face recognition)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

INSTALLATION
------------
1. Extract all files to a folder on your computer
2. Double-click Run_FaceAttendanceSystem.bat (Windows)
   or run ./run_faceattendance.sh (Linux/Mac)
3. Or navigate to FaceAttendanceSystem folder and run the executable
4. Default login credentials:
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
- Windows: C:\\Users\\<YourUsername>\\AppData\\Local\\FaceAttendanceSystem\\
- Linux: ~/.FaceAttendanceSystem/
- macOS: ~/Library/Application Support/FaceAttendanceSystem/

TROUBLESHOOTING
---------------
1. If the application doesn't start:
   - Check system requirements
   - Run as Administrator (Windows)
   - Check permissions (Linux/Mac)
   - Disable antivirus temporarily

2. If camera doesn't work:
   - Check camera permissions in system settings
   - Ensure no other application is using the camera

3. If face recognition is slow:
   - Close other applications
   - Ensure good lighting
   - Move closer to the camera

4. Display scaling issues (Windows):
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
Built with PyInstaller
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def print_summary(self):
        """Print build summary."""
        self.step(7, 7, "Build Summary")
        
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
        print(f"\n✓ Application ready: {self.output_dir / 'FaceAttendanceSystem'}")
        print(f"✓ Package ready: {self.output_dir}")
        print("\nNext steps:")
        print("  1. Test the application")
        print("  2. Create installer (optional)")
        print("  3. Distribute the package")
        
        return True
    
    def build(self):
        """Execute the full build process."""
        self.print_header("FACE RECOGNITION ATTENDANCE SYSTEM - PYINSTALLER BUILD")
        
        print(f"Project root: {self.project_root}")
        print(f"Output directory: {self.output_dir}")
        print(f"Python version: {sys.version}")
        print(f"Platform: {sys.platform}")
        
        steps = [
            (self.clean_build_dirs, self.args.clean),
            (self.prepare_models, True),
            (self.install_pyinstaller, True),
            (self.create_spec_file, True),
            (self.build_with_pyinstaller, True),
            (self.create_package_structure, True),
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
        description='Build Face Recognition Attendance System executable with PyInstaller'
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Full build with model preparation')
    parser.add_argument('--skip-models', action='store_true',
                       help='Skip model preparation (use existing)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean build directories before building')
    parser.add_argument('--onefile', action='store_true',
                       help='Create single-file executable (not recommended for this app)')
    parser.add_argument('--onedir', action='store_true', default=True,
                       help='Create one-directory bundle (default, recommended)')
    
    args = parser.parse_args()
    
    # --full implies --clean
    if args.full:
        args.clean = True
    
    # Build
    builder = PyInstallerBuilder(args)
    success = builder.build()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
