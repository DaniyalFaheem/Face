"""
resource_manager.py - Resource path management for frozen/compiled executables

This module handles path resolution for both development and frozen/compiled
environments. It supports PyInstaller and Nuitka packaging systems.

Features:
- Automatic detection of frozen execution
- Proper path resolution for bundled resources
- Writable directory management (AppData on Windows)
- OpenCV cascade file path handling

Usage:
    from resource_manager import ResourceManager
    
    rm = ResourceManager()
    cascade_path = rm.get_resource_path('haarcascade_frontalface_alt2.xml')
    db_path = rm.get_writable_path('face_database')
"""

import os
import sys
import shutil
from pathlib import Path


class ResourceManager:
    """Manages resource paths for both development and frozen environments."""
    
    def __init__(self, app_name='FaceAttendanceSystem'):
        """
        Initialize the resource manager.
        
        Args:
            app_name: Name of the application (used for AppData directory)
        """
        self.app_name = app_name
        self._is_frozen = self._detect_frozen()
        self._bundle_dir = self._get_bundle_dir()
        self._writable_dir = self._get_writable_dir()
        
        # Ensure writable directory exists
        self._writable_dir.mkdir(parents=True, exist_ok=True)
        
    def _detect_frozen(self):
        """
        Detect if the application is running as a frozen executable.
        
        Returns:
            bool: True if frozen, False if running as script
        """
        # PyInstaller frozen
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return True
        
        # Nuitka frozen
        if '__compiled__' in globals():
            return True
        
        # Check sys.frozen attribute (set by PyInstaller and some others)
        if getattr(sys, 'frozen', False):
            return True
        
        return False
    
    def _get_bundle_dir(self):
        """
        Get the directory where bundled resources are located.
        
        Returns:
            Path: Path to the bundle directory
        """
        if self._is_frozen:
            # PyInstaller temp folder
            if hasattr(sys, '_MEIPASS'):
                return Path(sys._MEIPASS)
            
            # Nuitka: executable directory
            if getattr(sys, 'frozen', False):
                return Path(sys.executable).parent
            
        # Development: script directory
        return Path(__file__).parent
    
    def _get_writable_dir(self):
        """
        Get a writable directory for the application.
        
        On Windows, uses AppData\Local\{app_name}
        On other systems, uses ~/.{app_name}
        In development mode, uses the script directory
        
        Returns:
            Path: Path to the writable directory
        """
        if not self._is_frozen:
            # Development mode: use script directory
            return Path(__file__).parent
        
        # Frozen mode: use system-specific writable location
        if sys.platform == 'win32':
            # Windows: Use AppData\Local
            appdata = os.getenv('LOCALAPPDATA')
            if not appdata:
                appdata = os.path.join(os.getenv('USERPROFILE', ''), 'AppData', 'Local')
            return Path(appdata) / self.app_name
        else:
            # Linux/Mac: Use home directory
            return Path.home() / f'.{self.app_name}'
    
    def get_resource_path(self, relative_path):
        """
        Get the absolute path to a bundled resource.
        
        Args:
            relative_path: Relative path to the resource
            
        Returns:
            Path: Absolute path to the resource
        """
        resource = self._bundle_dir / relative_path
        
        if resource.exists():
            return resource
        
        # If not found in bundle, check writable directory
        writable_resource = self._writable_dir / relative_path
        if writable_resource.exists():
            return writable_resource
        
        # Return bundle path anyway (may not exist yet)
        return resource
    
    def get_writable_path(self, relative_path=''):
        """
        Get a writable path for the application.
        
        Use this for files that need to be created/modified at runtime
        (e.g., database, CSV files, logs).
        
        Args:
            relative_path: Relative path within the writable directory
            
        Returns:
            Path: Absolute path to the writable location
        """
        if relative_path:
            path = self._writable_dir / relative_path
        else:
            path = self._writable_dir
        
        # Create parent directories if they don't exist
        if relative_path and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def get_opencv_cascade_path(self, cascade_name):
        """
        Get the path to an OpenCV cascade file.
        
        Handles both development (using cv2.data.haarcascades) and
        frozen environments (using bundled files).
        
        Args:
            cascade_name: Name of the cascade file (e.g., 'haarcascade_frontalface_alt2.xml')
            
        Returns:
            str: Full path to the cascade file
        """
        # First, try bundled cascade
        bundled_cascade = self.get_resource_path(cascade_name)
        if bundled_cascade.exists():
            return str(bundled_cascade)
        
        # Try in cascades subdirectory
        bundled_cascade = self.get_resource_path(f'cascades/{cascade_name}')
        if bundled_cascade.exists():
            return str(bundled_cascade)
        
        # In development, use cv2.data.haarcascades
        if not self._is_frozen:
            try:
                import cv2
                cv2_cascade_path = os.path.join(cv2.data.haarcascades, cascade_name)
                if os.path.exists(cv2_cascade_path):
                    return cv2_cascade_path
            except (ImportError, AttributeError):
                pass
        
        # Fallback: return bundled path (may not exist)
        return str(bundled_cascade)
    
    def copy_resource_if_missing(self, relative_path, source=None):
        """
        Copy a resource from bundle to writable directory if it doesn't exist.
        
        Useful for initializing user-editable files.
        
        Args:
            relative_path: Relative path to the resource
            source: Optional source path (defaults to bundle)
            
        Returns:
            Path: Path to the resource in writable directory
        """
        dest = self.get_writable_path(relative_path)
        
        if not dest.exists():
            if source is None:
                source = self.get_resource_path(relative_path)
            
            if source.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                if source.is_file():
                    shutil.copy2(source, dest)
                else:
                    shutil.copytree(source, dest)
        
        return dest
    
    def is_frozen(self):
        """
        Check if running as a frozen executable.
        
        Returns:
            bool: True if frozen, False if running as script
        """
        return self._is_frozen
    
    def get_bundle_dir(self):
        """
        Get the bundle directory path.
        
        Returns:
            Path: Path to the bundle directory
        """
        return self._bundle_dir
    
    def get_writable_dir(self):
        """
        Get the writable directory path.
        
        Returns:
            Path: Path to the writable directory
        """
        return self._writable_dir
    
    def ensure_directory_structure(self):
        """
        Ensure all required directories exist in the writable location.
        
        Creates:
        - face_database/
        - logs/
        """
        directories = ['face_database', 'logs']
        
        for directory in directories:
            dir_path = self.get_writable_path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_info(self):
        """
        Get information about the resource manager configuration.
        
        Returns:
            dict: Configuration information
        """
        return {
            'is_frozen': self._is_frozen,
            'bundle_dir': str(self._bundle_dir),
            'writable_dir': str(self._writable_dir),
            'app_name': self.app_name,
            'platform': sys.platform,
        }


# Global instance for easy access
_resource_manager = None


def get_resource_manager(app_name='FaceAttendanceSystem'):
    """
    Get or create the global ResourceManager instance.
    
    Args:
        app_name: Name of the application
        
    Returns:
        ResourceManager: The global resource manager instance
    """
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager(app_name)
    return _resource_manager


# Convenience functions for quick access
def get_resource_path(relative_path):
    """Get path to a bundled resource."""
    return get_resource_manager().get_resource_path(relative_path)


def get_writable_path(relative_path=''):
    """Get path to a writable location."""
    return get_resource_manager().get_writable_path(relative_path)


def is_frozen():
    """Check if running as frozen executable."""
    return get_resource_manager().is_frozen()


if __name__ == '__main__':
    # Test/demo code
    print("Resource Manager Information")
    print("=" * 60)
    
    rm = get_resource_manager()
    info = rm.get_info()
    
    for key, value in info.items():
        print(f"{key:20s}: {value}")
    
    print("\n" + "=" * 60)
    print("Example paths:")
    print(f"  Resource (cascade): {rm.get_opencv_cascade_path('haarcascade_frontalface_alt2.xml')}")
    print(f"  Writable (DB):      {rm.get_writable_path('face_database')}")
    print(f"  Writable (CSV):     {rm.get_writable_path('student_attendance.csv')}")
