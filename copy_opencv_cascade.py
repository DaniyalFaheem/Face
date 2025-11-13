"""
copy_opencv_cascade.py - Copy OpenCV cascade files to project directory

This script copies the haarcascade_frontalface_alt2.xml file from the
OpenCV installation to the project directory for bundling.

Run this after installing OpenCV:
    python copy_opencv_cascade.py
"""

import os
import shutil
import sys


def copy_cascade():
    """Copy cascade file from OpenCV to project directory."""
    try:
        import cv2
        
        cascade_name = 'haarcascade_frontalface_alt2.xml'
        src_path = os.path.join(cv2.data.haarcascades, cascade_name)
        dest_path = os.path.join(os.path.dirname(__file__), cascade_name)
        
        if not os.path.exists(src_path):
            print(f"❌ ERROR: Cascade file not found in OpenCV: {src_path}")
            return False
        
        print(f"Copying cascade file...")
        print(f"  Source: {src_path}")
        print(f"  Destination: {dest_path}")
        
        shutil.copy2(src_path, dest_path)
        
        print(f"✓ Cascade file copied successfully")
        print(f"  Size: {os.path.getsize(dest_path) / 1024:.1f} KB")
        
        return True
        
    except ImportError:
        print("❌ ERROR: OpenCV (cv2) is not installed")
        print("Please install it first: pip install opencv-python")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to copy cascade file: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("OpenCV Cascade Copy Tool")
    print("=" * 60 + "\n")
    
    success = copy_cascade()
    
    sys.exit(0 if success else 1)
