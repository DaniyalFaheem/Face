# How to Build EXE Using GitHub Actions

This guide explains how to build the executable file automatically using GitHub Actions - **no local setup required!**

## 🎯 Why Use GitHub Actions?

- ✅ **No setup needed** - No Python, no Visual Studio, nothing to install
- ✅ **Automatic builds** - Builds run on GitHub's servers
- ✅ **Always works** - Clean environment every time
- ✅ **Free** - For public repositories
- ✅ **Multi-platform** - Builds for Windows and Linux simultaneously

## 📋 Prerequisites

1. GitHub account
2. This repository (forked or yours)
3. Internet connection
4. That's it!

## 🚀 Step-by-Step Instructions

### Method 1: Manual Workflow Trigger (Recommended)

This is the easiest way to build on-demand.

#### Step 1: Navigate to Actions
1. Go to your repository on GitHub
2. Click the **"Actions"** tab at the top
3. You'll see a list of workflows

#### Step 2: Run the Build Workflow
1. Click on **"Build Executable"** in the left sidebar
2. You'll see a button **"Run workflow"** on the right
3. Click the **"Run workflow"** button
4. A dialog appears with options:
   - **Branch**: Select `main` or `master` (your default branch)
   - **Skip model download**: 
     - Select `false` for full build with AI models (~500MB)
     - Select `true` for faster build without models (testing only)
5. Click the green **"Run workflow"** button

#### Step 3: Monitor the Build
1. The workflow will appear in the list (yellow dot = running)
2. Click on it to see real-time progress
3. You'll see two jobs:
   - **Build Windows Executable**
   - **Build Linux Executable**
4. Both run simultaneously (takes ~20-30 minutes)

#### Step 4: Download the Executable
1. When complete (green checkmark ✅), scroll down to **"Artifacts"**
2. You'll see:
   - `FaceAttendanceSystem-Windows` - Windows executable
   - `FaceAttendanceSystem-Linux` - Linux executable
   - (On main branch pushes) `FaceAttendanceSystem-Release-ZIP` - Distribution package
3. Click on the artifact to download
4. Extract the ZIP file
5. Your executable is ready!

### Method 2: Automatic Build on Push

The workflow automatically runs when you push code changes.

#### Triggers
The build automatically runs when:
- You push commits to `main` or `master` branch
- The push includes changes to:
  - Any Python file (`.py`)
  - Build configuration files
  - The workflow file itself

#### What Happens
1. GitHub detects the push
2. Workflow starts automatically
3. Builds for both Windows and Linux
4. Uploads artifacts
5. Creates release packages (ZIP/tar.gz)

#### Where to Find Results
1. Go to **Actions** tab
2. Click on the most recent workflow run
3. Download artifacts as described above

## 📦 What You Get

### Windows Build Artifact
```
FaceAttendanceSystem-Windows.zip (downloaded artifact)
└── FaceAttendanceSystem_Package/
    ├── FaceAttendanceSystem/
    │   ├── FaceAttendanceSystem.exe    ← Main executable
    │   └── ... (dependencies)
    ├── README.txt
    ├── QUICKSTART.txt
    ├── USER_GUIDE.md
    ├── face_database/
    └── Run_FaceAttendanceSystem.bat    ← Easy launcher
```

### Linux Build Artifact
```
FaceAttendanceSystem-Linux.tar.gz (downloaded artifact)
└── FaceAttendanceSystem_Package/
    ├── FaceAttendanceSystem/
    │   ├── FaceAttendanceSystem        ← Main executable
    │   └── ... (dependencies)
    ├── README.txt
    ├── USER_GUIDE.md
    ├── face_database/
    └── run_faceattendance.sh           ← Easy launcher
```

## ▶️ Running the Executable

### Windows
1. Extract `FaceAttendanceSystem-Windows.zip`
2. Go into `FaceAttendanceSystem_Package` folder
3. Double-click `Run_FaceAttendanceSystem.bat`
4. Application launches!

**Alternative**:
1. Go into `FaceAttendanceSystem` subfolder
2. Double-click `FaceAttendanceSystem.exe`

### Linux
1. Extract `FaceAttendanceSystem-Linux.tar.gz`
2. Open terminal in `FaceAttendanceSystem_Package` folder
3. Run: `./run_faceattendance.sh`
4. Application launches!

**Alternative**:
```bash
cd FaceAttendanceSystem_Package/FaceAttendanceSystem
chmod +x FaceAttendanceSystem
./FaceAttendanceSystem
```

## 🔍 Monitoring Build Progress

### View Build Logs
1. Click on the running workflow
2. Click on a job (Windows or Linux)
3. Expand steps to see detailed logs:
   - ✅ Checkout code
   - ✅ Set up Python 3.8
   - ✅ Install dependencies
   - ✅ Prepare models (if not skipped)
   - ✅ Build with PyInstaller
   - ✅ Upload artifacts

### Check Build Status
- 🟡 **Yellow dot** = Building (in progress)
- ✅ **Green checkmark** = Success
- ❌ **Red X** = Failed (check logs)

## 🐛 Troubleshooting

### Workflow Not Appearing
**Problem**: Can't see "Build Executable" workflow

**Solution**:
1. Make sure the file `.github/workflows/build-exe.yml` exists in your repo
2. Push it if missing
3. Refresh the Actions page

### Build Fails
**Problem**: Build completes but shows red X

**Solution**:
1. Click on the failed job
2. Read the error logs
3. Common issues:
   - **Model download failed**: Enable "Skip model download" option
   - **Dependency error**: Check requirements-build.txt
   - **Python version**: Workflow uses Python 3.8 (should work)

### Can't Download Artifacts
**Problem**: Artifacts not showing or can't download

**Solution**:
1. Make sure build completed successfully (green checkmark)
2. Scroll down to "Artifacts" section at the bottom
3. Artifacts expire after 30 days (default)
4. For releases, artifacts kept for 90 days

### Large Build Size
**Problem**: Downloaded file is very large (~300MB+)

**Solution**: This is normal! The package includes:
- Application executable
- All Python libraries
- AI models for face recognition (~500MB)
- All dependencies bundled

## ⚙️ Advanced: Customizing the Workflow

### Edit Workflow File
Location: `.github/workflows/build-exe.yml`

### Change Python Version
```yaml
- name: Set up Python 3.8
  uses: actions/setup-python@v5
  with:
    python-version: '3.8'  # Change this to 3.9, 3.10, 3.11, or 3.12
```

### Change Artifact Retention
```yaml
- name: Upload build artifact
  uses: actions/upload-artifact@v4
  with:
    name: FaceAttendanceSystem-Windows
    path: dist/FaceAttendanceSystem_Package/
    retention-days: 30  # Change to 1-90 days
```

### Skip Model Download by Default
```yaml
on:
  workflow_dispatch:
    inputs:
      skip_models:
        default: 'true'  # Change from 'false' to 'true'
```

## 📊 Build Times

Typical build times on GitHub Actions:

| Stage | Time |
|-------|------|
| Setup Python & Dependencies | 2-5 min |
| Download Models (if enabled) | 5-10 min |
| PyInstaller Build | 10-15 min |
| Package & Upload | 2-5 min |
| **Total** | **20-35 min** |

**Note**: Both Windows and Linux build in parallel, so total time is ~20-35 minutes regardless.

## 💡 Tips

1. **First build**: Always include models (skip_models: false)
2. **Testing builds**: Use skip_models: true for faster iteration
3. **Production builds**: Always run on main/master branch
4. **Distribution**: Use the Release artifacts (ZIP/tar.gz)
5. **Download promptly**: Artifacts expire after 30 days

## 🎉 Success!

Once you download and extract the artifact:

1. ✅ Executable is ready to use
2. ✅ All dependencies included
3. ✅ AI models bundled (if not skipped)
4. ✅ No Python installation needed on target machine
5. ✅ Ready for distribution to end users

## 📚 Additional Resources

- **Quick Build Guide**: [QUICK_BUILD.md](QUICK_BUILD.md)
- **Full Build Documentation**: [BUILDING.md](BUILDING.md)
- **User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **GitHub Actions Docs**: https://docs.github.com/en/actions

---

**Questions?** Create an issue on GitHub or check the documentation.

**Last Updated**: November 2024
