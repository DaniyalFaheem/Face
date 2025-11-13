# Face Recognition Attendance System

A comprehensive face recognition-based attendance management system with automated WhatsApp notifications and salary calculations.

## Features

- 🎯 Real-time face recognition using DeepFace (VGG-Face model)
- 👤 Separate Student and Faculty management
- 📊 Attendance tracking with CSV exports
- 📱 Automated WhatsApp notifications for absentees
- 💰 Automated salary calculation for faculty
- 🎨 Modern GUI with Tkinter
- 🔒 Role-based access control (Admin/User)

## System Requirements

### Development
- Python 3.8.x (Required for TensorFlow compatibility)
- Webcam
- 8GB RAM minimum (16GB recommended)
- Windows 10/11, Linux, or macOS

### Runtime (Standalone Executable)
- Windows 10/11
- Webcam
- 4GB RAM minimum
- No Python installation required

## Quick Start

### For Users (Standalone Executable)

1. Download the latest release
2. Extract the ZIP file
3. Run `FaceAttendanceSystem.exe`
4. Login with default credentials:
   - Admin: `admin` / `admin123`
   - User: `user` / `user123`

### For Developers

#### Installation

```bash
# Clone the repository
git clone https://github.com/DaniyalFaheem/Face.git
cd Face

# Create virtual environment (Python 3.8 required!)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements-build.txt
```

#### Running from Source

```bash
python app.py
```

## Building Standalone Executable

See [QUICK_BUILD.md](QUICK_BUILD.md) for a simple guide or [BUILDING.md](BUILDING.md) for complete instructions.

### Method 1: GitHub Actions (Easiest - No Setup!)

1. Go to **Actions** tab on GitHub
2. Run **"Build Executable"** workflow
3. Download the built executable artifact

### Method 2: PyInstaller (Cross-Platform)

```bash
# Install PyInstaller
pip install pyinstaller

# Build (works with Python 3.8-3.12)
python build_pyinstaller.py --full --clean
```

Output: `dist/FaceAttendanceSystem_Package/`

### Method 3: Nuitka (Windows, Optimized)

```bash
# Windows: One-click build
build.bat

# Or manually (requires Python 3.8 exactly)
python build.py --full
```

Output: `dist/FaceAttendanceSystem_Package/`

### Build Options

```bash
# PyInstaller - Full build
python build_pyinstaller.py --full --clean

# Nuitka - Full build with model preparation
python build.py --full

# Skip model download (use existing)
python build_pyinstaller.py --skip-models
```

## Architecture

### Packaging Solution

The project includes a comprehensive packaging solution for creating standalone executables:

1. **prepare_models.py** - Downloads and prepares AI models (~500MB)
2. **resource_manager.py** - Handles paths for frozen/development environments
3. **config.py** - Centralized configuration and environment setup
4. **build.py** - Automated build process using Nuitka
5. **app_launcher.py** - Application entry point wrapper
6. **test_standalone.py** - Validation framework for testing builds

### Key Components

- **DeepFace**: Face recognition (VGG-Face model, SSD detector)
- **OpenCV**: Computer vision and face detection
- **TensorFlow**: Deep learning backend
- **Tkinter**: GUI framework
- **Pandas**: Data management
- **PyAutoGUI**: WhatsApp automation

## Project Structure

```
Face/
├── app.py                      # Main application
├── app_launcher.py             # Entry point for executable
├── prepare_models.py           # Model preparation
├── resource_manager.py         # Path management
├── config.py                   # Configuration
├── build.py                    # Build automation
├── test_standalone.py          # Validation tests
├── requirements-build.txt      # Build dependencies
├── build.bat                   # Windows build script
├── BUILDING.md                 # Build documentation
├── copy_opencv_cascade.py      # OpenCV helper
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Usage

### Admin Panel

1. **Register Users**
   - Click "Register New User"
   - Select Student or Faculty
   - Fill in details
   - Capture face samples (80 images)

2. **Manage Users**
   - View all registered users
   - Delete users
   - View user details and photos

3. **Attendance**
   - System automatically recognizes faces
   - Click "Mark Attendance" to log
   - View logs by category (Student/Faculty)

4. **Absentee Alerts**
   - View absent users
   - Send WhatsApp notifications
   - Requires `send_button.png` screenshot

5. **Salary Calculation**
   - Select date range
   - Calculate based on attendance
   - Export to CSV

### User Panel

- Register students only
- View student attendance
- Mark attendance

## Configuration

### Default Credentials

Change these in production:
- Admin: `admin` / `admin123`
- User: `user` / `user123`

### Model Configuration

Edit `config.py` to change:
- Face recognition model (default: VGG-Face)
- Detector backend (default: SSD)
- Distance threshold (default: 0.40)
- Recognition interval (default: 0.75s)

### Performance Tuning

In `config.py`:
```python
RECOGNITION_INTERVAL = 0.75     # Recognition delay (seconds)
FRAME_SCALE_FACTOR = 0.5        # Frame processing scale
CONFIDENCE_THRESHOLD = 0.75     # Recognition confidence
LOG_COOLDOWN_SECONDS = 300      # Attendance cooldown (5 min)
```

## Data Storage

### Development Mode
All data stored in project directory:
- `face_database/` - Face images
- `*.csv` - Attendance logs
- `*.pkl` - Model cache

### Standalone Executable
Data stored in:
- Windows: `C:\Users\<User>\AppData\Local\FaceAttendanceSystem\`
- Linux: `~/.FaceAttendanceSystem/`

## Troubleshooting

### Python Version Error
**Issue**: `TypeError: unhashable type: 'list'`

**Solution**: Use Python 3.8.x. TensorFlow has compatibility issues with 3.9+.

### Display Scaling Error
**Issue**: `needle exceeds haystack` in PyAutoGUI

**Solution**: The app sets DPI awareness automatically. If issues persist:
1. Set Windows display scaling to 100%
2. Or disable PyAutoGUI features

### Camera Not Working
1. Check camera permissions in system settings
2. Ensure no other app is using the camera
3. Try different camera index in code

### Face Recognition Slow
1. Reduce `FRAME_SCALE_FACTOR` in config
2. Increase `RECOGNITION_INTERVAL`
3. Ensure good lighting
4. Close other applications

### Build Failures
See [BUILDING.md](BUILDING.md) for detailed troubleshooting.

## Testing

```bash
# Run all validation tests
python test_standalone.py --verbose

# Test resource manager
python resource_manager.py

# Test configuration
python config.py

# Test model preparation
python prepare_models.py
```

## Dependencies

### Core
- deepface >= 0.0.79
- tensorflow >= 2.13.0, < 2.14.0
- opencv-python >= 4.8.0
- pandas >= 2.0.0
- numpy >= 1.24.0, < 2.0.0
- Pillow >= 10.0.0

### Automation
- pywhatkit >= 5.4
- pyautogui >= 0.9.54

### Build
- nuitka >= 1.8.0
- ordered-set >= 4.1.0

See `requirements-build.txt` for complete list.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See LICENSE file for details.

## Acknowledgments

- **DeepFace**: Serengil, S. I., & Ozpinar, A. (2020). LightFace: A Hybrid Deep Face Recognition Framework. In 2020 Innovations in Intelligent Systems and Applications Conference (ASYU).
- **OpenCV**: Open Source Computer Vision Library
- **TensorFlow**: Google Brain Team

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Check [BUILDING.md](BUILDING.md) for build help
- Review validation logs in `validation_report.json`

## Version History

### Version 1.0.0 (2024)
- Initial release
- Complete packaging solution
- VGG-Face model support
- Windows executable build
- Student and Faculty management
- WhatsApp notifications
- Salary calculations

---

**Maintained by**: DaniyalFaheem  
**Last Updated**: November 2024
