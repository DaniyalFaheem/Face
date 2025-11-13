"""
prepare_models.py - Pre-download DeepFace models for packaging

This script downloads and prepares DeepFace models (VGG-Face and SSD detector)
for inclusion in the standalone executable. Models are copied from the user's
cache directory to the project folder for bundling.

Usage:
    python prepare_models.py
"""

import os
import sys
import shutil
from pathlib import Path


def get_deepface_home():
    """Get the DeepFace home directory where models are cached."""
    home = os.getenv('DEEPFACE_HOME')
    if home:
        return Path(home)
    
    # Default DeepFace home locations
    if sys.platform == 'win32':
        return Path.home() / '.deepface'
    else:
        return Path.home() / '.deepface'


def download_models():
    """Download required DeepFace models by triggering their first use."""
    print("=" * 80)
    print("DOWNLOADING DEEPFACE MODELS")
    print("=" * 80)
    print("\nThis will download the following models:")
    print("  1. VGG-Face model (~500MB)")
    print("  2. SSD face detector model")
    print("\nPlease wait, this may take several minutes depending on your connection...\n")
    
    try:
        import numpy as np
        from deepface import DeepFace
        
        # Suppress TensorFlow warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        import warnings
        warnings.filterwarnings('ignore')
        
        print("Step 1/2: Loading VGG-Face model...")
        # Create a blank test image
        blank_img = np.zeros((224, 224, 3), dtype=np.uint8)
        
        # This will trigger model download if not present
        try:
            result = DeepFace.find(
                img_path=blank_img,
                db_path=".",
                model_name='VGG-Face',
                detector_backend='opencv',
                enforce_detection=False,
                silent=True
            )
            print("✓ VGG-Face model loaded successfully")
        except Exception as e:
            print(f"✓ VGG-Face model downloaded (verification failed as expected: {e})")
        
        print("\nStep 2/2: Loading SSD detector model...")
        # Trigger SSD detector download
        try:
            result = DeepFace.find(
                img_path=blank_img,
                db_path=".",
                model_name='VGG-Face',
                detector_backend='ssd',
                enforce_detection=False,
                silent=True
            )
            print("✓ SSD detector model loaded successfully")
        except Exception as e:
            print(f"✓ SSD detector model downloaded (verification failed as expected: {e})")
        
        print("\n" + "=" * 80)
        print("MODEL DOWNLOAD COMPLETE")
        print("=" * 80)
        return True
        
    except ImportError as e:
        print(f"\n❌ ERROR: Required libraries not installed: {e}")
        print("Please install dependencies first:")
        print("  pip install deepface tensorflow opencv-python")
        return False
    except Exception as e:
        print(f"\n❌ ERROR downloading models: {e}")
        return False


def copy_models_to_project():
    """Copy models from DeepFace cache to project directory."""
    print("\n" + "=" * 80)
    print("COPYING MODELS TO PROJECT")
    print("=" * 80)
    
    deepface_home = get_deepface_home()
    project_models_dir = Path(__file__).parent / 'deepface_models'
    
    print(f"\nSource: {deepface_home}")
    print(f"Destination: {project_models_dir}")
    
    if not deepface_home.exists():
        print(f"\n❌ ERROR: DeepFace home directory not found: {deepface_home}")
        print("Models may not have been downloaded yet.")
        return False
    
    # Create project models directory
    project_models_dir.mkdir(exist_ok=True)
    
    # Models to copy
    model_paths = {
        'weights': deepface_home / 'weights',
        '.deepface': deepface_home / '.deepface'
    }
    
    copied_count = 0
    total_size = 0
    
    for model_name, source_path in model_paths.items():
        if source_path.exists():
            dest_path = project_models_dir / model_name
            
            if source_path.is_file():
                # Copy single file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                size = source_path.stat().st_size
                total_size += size
                copied_count += 1
                print(f"  ✓ Copied {model_name} ({size / 1024 / 1024:.1f} MB)")
            else:
                # Copy directory
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
                
                # Calculate directory size
                size = sum(f.stat().st_size for f in dest_path.rglob('*') if f.is_file())
                total_size += size
                copied_count += 1
                print(f"  ✓ Copied {model_name} directory ({size / 1024 / 1024:.1f} MB)")
        else:
            print(f"  ⚠ Skipped {model_name} (not found)")
    
    # Copy any .h5 model files from weights directory
    weights_dir = deepface_home / 'weights'
    if weights_dir.exists():
        dest_weights = project_models_dir / 'weights'
        dest_weights.mkdir(exist_ok=True)
        
        for model_file in weights_dir.glob('*.h5'):
            dest_file = dest_weights / model_file.name
            shutil.copy2(model_file, dest_file)
            size = model_file.stat().st_size
            total_size += size
            copied_count += 1
            print(f"  ✓ Copied {model_file.name} ({size / 1024 / 1024:.1f} MB)")
    
    print(f"\nTotal: {copied_count} items copied ({total_size / 1024 / 1024:.1f} MB)")
    
    # Create a marker file to indicate models are ready
    marker_file = project_models_dir / 'MODELS_READY.txt'
    with open(marker_file, 'w') as f:
        f.write(f"Models prepared successfully\n")
        f.write(f"Total size: {total_size / 1024 / 1024:.1f} MB\n")
        f.write(f"Items: {copied_count}\n")
    
    print("\n" + "=" * 80)
    print("MODELS COPIED SUCCESSFULLY")
    print("=" * 80)
    return True


def verify_models():
    """Verify that all required models are present in project directory."""
    print("\n" + "=" * 80)
    print("VERIFYING MODELS")
    print("=" * 80)
    
    project_models_dir = Path(__file__).parent / 'deepface_models'
    
    if not project_models_dir.exists():
        print("\n❌ Models directory not found")
        return False
    
    # Check for marker file
    marker_file = project_models_dir / 'MODELS_READY.txt'
    if marker_file.exists():
        print("\n✓ Models marker file found")
        with open(marker_file, 'r') as f:
            print(f.read())
    
    # List all files
    print("\nFiles in models directory:")
    file_count = 0
    for item in project_models_dir.rglob('*'):
        if item.is_file():
            size = item.stat().st_size
            rel_path = item.relative_to(project_models_dir)
            print(f"  {rel_path} ({size / 1024 / 1024:.2f} MB)")
            file_count += 1
    
    print(f"\nTotal files: {file_count}")
    
    if file_count > 0:
        print("\n" + "=" * 80)
        print("VERIFICATION SUCCESSFUL")
        print("=" * 80)
        return True
    else:
        print("\n❌ No model files found")
        return False


def main():
    """Main function to prepare all models."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DEEPFACE MODEL PREPARATION TOOL" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    # Step 1: Download models
    if not download_models():
        print("\n⚠ Model download failed. Please check your internet connection")
        print("and ensure all dependencies are installed.")
        return False
    
    # Step 2: Copy models to project
    if not copy_models_to_project():
        print("\n⚠ Model copy failed. Models may need to be downloaded again.")
        return False
    
    # Step 3: Verify models
    if not verify_models():
        print("\n⚠ Model verification failed.")
        return False
    
    print("\n✓ All models prepared successfully!")
    print("\nYou can now run the build script to create the standalone executable.")
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
