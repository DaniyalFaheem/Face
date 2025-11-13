"""
config.py - Centralized configuration for standalone execution

This module sets up the environment for the Face Recognition Attendance System
to work correctly in both development and frozen/compiled environments.

Features:
- Environment variable configuration
- TensorFlow/DeepFace path setup
- Platform-specific DLL management
- Directory initialization
- Model cache configuration

Usage:
    from config import setup_environment
    
    setup_environment()  # Call before importing other modules
"""

import os
import sys
from pathlib import Path


def setup_environment(resource_manager=None):
    """
    Set up the environment for the application.
    
    This should be called at the very start of the application, before
    importing TensorFlow, DeepFace, or OpenCV.
    
    Args:
        resource_manager: Optional ResourceManager instance
    """
    # Import here to avoid circular dependency
    if resource_manager is None:
        from resource_manager import get_resource_manager
        resource_manager = get_resource_manager()
    
    print("Setting up environment...")
    
    # 1. Suppress TensorFlow warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    
    # 2. Set DeepFace home to bundled models or writable directory
    if resource_manager.is_frozen():
        # In frozen mode, check if models are bundled
        bundled_models = resource_manager.get_resource_path('deepface_models')
        if bundled_models.exists():
            print(f"  Using bundled models: {bundled_models}")
            os.environ['DEEPFACE_HOME'] = str(bundled_models)
        else:
            # Use writable directory for model cache
            models_dir = resource_manager.get_writable_path('models')
            models_dir.mkdir(parents=True, exist_ok=True)
            print(f"  Using writable models directory: {models_dir}")
            os.environ['DEEPFACE_HOME'] = str(models_dir)
    else:
        # Development mode: check for project models first
        project_models = Path(__file__).parent / 'deepface_models'
        if project_models.exists():
            print(f"  Using project models: {project_models}")
            os.environ['DEEPFACE_HOME'] = str(project_models)
        # Otherwise, let DeepFace use default location
    
    # 3. Set OpenCV environment variables
    if resource_manager.is_frozen():
        bundle_dir = resource_manager.get_bundle_dir()
        os.environ['OPENCV_DATA_PATH'] = str(bundle_dir)
    
    # 4. Configure paths in sys.path if needed
    bundle_dir = resource_manager.get_bundle_dir()
    if str(bundle_dir) not in sys.path:
        sys.path.insert(0, str(bundle_dir))
    
    # 5. Ensure required directories exist
    resource_manager.ensure_directory_structure()
    
    print("  Environment setup complete")
    return resource_manager


def get_application_paths(resource_manager=None):
    """
    Get all important application paths.
    
    Args:
        resource_manager: Optional ResourceManager instance
        
    Returns:
        dict: Dictionary of application paths
    """
    if resource_manager is None:
        from resource_manager import get_resource_manager
        resource_manager = get_resource_manager()
    
    return {
        # Writable paths (for data that changes)
        'db_path': str(resource_manager.get_writable_path('face_database')),
        'student_attendance_file': str(resource_manager.get_writable_path('student_attendance.csv')),
        'faculty_attendance_file': str(resource_manager.get_writable_path('faculty_attendance.csv')),
        'salary_file': str(resource_manager.get_writable_path('salary.csv')),
        'logs_dir': str(resource_manager.get_writable_path('logs')),
        
        # Resource paths (read-only bundled files)
        'cascade_file': resource_manager.get_opencv_cascade_path('haarcascade_frontalface_alt2.xml'),
        'send_button_image': str(resource_manager.get_resource_path('send_button.png')),
        'background_image': str(resource_manager.get_resource_path('background.jpg')),
        
        # Directory paths
        'bundle_dir': str(resource_manager.get_bundle_dir()),
        'writable_dir': str(resource_manager.get_writable_dir()),
    }


def setup_dpi_awareness():
    """
    Set up DPI awareness for Windows to handle display scaling correctly.
    
    This prevents the 'needle exceeds haystack' error in PyAutoGUI.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            # Set process DPI awareness
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            print("  DPI awareness enabled")
        except Exception as e:
            print(f"  Warning: Could not set DPI awareness: {e}")


def check_dependencies():
    """
    Check if all required dependencies are available.
    
    Returns:
        tuple: (success: bool, missing: list)
    """
    required_modules = [
        'cv2',
        'pandas',
        'PIL',
        'numpy',
        'deepface',
        'pywhatkit',
        'pyautogui',
        'tensorflow',
    ]
    
    missing = []
    
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)
    
    return (len(missing) == 0, missing)


def initialize_application():
    """
    Complete application initialization sequence.
    
    This performs all setup steps needed for the application to run:
    1. Set up DPI awareness
    2. Configure environment variables
    3. Set up paths
    4. Check dependencies
    
    Returns:
        dict: Application configuration including paths and status
    """
    print("\n" + "=" * 60)
    print("INITIALIZING FACE RECOGNITION ATTENDANCE SYSTEM")
    print("=" * 60)
    
    # Step 1: DPI awareness
    setup_dpi_awareness()
    
    # Step 2: Environment setup
    from resource_manager import get_resource_manager
    rm = get_resource_manager()
    setup_environment(rm)
    
    # Step 3: Get paths
    paths = get_application_paths(rm)
    
    # Step 4: Check dependencies
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print("\n⚠ Warning: Missing dependencies:")
        for module in missing:
            print(f"    - {module}")
    
    print("\nConfiguration:")
    print(f"  Frozen mode:    {rm.is_frozen()}")
    print(f"  Bundle dir:     {rm.get_bundle_dir()}")
    print(f"  Writable dir:   {rm.get_writable_dir()}")
    print(f"  Database:       {paths['db_path']}")
    print(f"  Cascade file:   {paths['cascade_file']}")
    
    print("=" * 60 + "\n")
    
    return {
        'resource_manager': rm,
        'paths': paths,
        'dependencies_ok': deps_ok,
        'missing_dependencies': missing,
    }


# Configuration constants
APP_NAME = 'FaceAttendanceSystem'
APP_VERSION = '1.0.0'

# DeepFace model configuration
DEEPFACE_MODEL = 'VGG-Face'
DEEPFACE_DETECTOR = 'ssd'
DEEPFACE_METRIC = 'cosine'
DEEPFACE_THRESHOLD = 0.40

# Performance tuning
RECOGNITION_INTERVAL = 0.75
FRAME_SCALE_FACTOR = 0.5
DISPLAY_LOOP_MS = 15
HISTORY_MAX_LENGTH = 8
CONFIDENCE_THRESHOLD = 0.75
REQUIRED_STABLE_FRAMES = 4

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Attendance settings
LOG_COOLDOWN_SECONDS = 300  # 5 minutes

# UI Colors
COLOR_PRIMARY = "#2C3E50"
COLOR_SECONDARY = "#34495E"
COLOR_ACCENT = "#3498DB"
COLOR_SUCCESS = "#2ECC71"
COLOR_WARNING = "#F1C40F"
COLOR_DANGER = "#E74C3C"
COLOR_TEXT_LIGHT = "#ECF0F1"
COLOR_TEXT_DARK = "#2C3E50"
COLOR_INPUT_BG = "#404040"


if __name__ == '__main__':
    # Test configuration
    config = initialize_application()
    
    print("\nApplication Paths:")
    for key, value in config['paths'].items():
        print(f"  {key:25s}: {value}")
    
    if not config['dependencies_ok']:
        print("\n⚠ Some dependencies are missing!")
        print("Please install:")
        for dep in config['missing_dependencies']:
            print(f"  pip install {dep}")
    else:
        print("\n✓ All dependencies are available")
