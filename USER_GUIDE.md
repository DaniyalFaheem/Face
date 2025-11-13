# Complete User Guide - Face Recognition Attendance System

## Table of Contents
1. [Getting Started](#getting-started)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [First Run](#first-run)
5. [User Registration](#user-registration)
6. [Attendance Marking](#attendance-marking)
7. [Admin Features](#admin-features)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Getting Started

### What is This Application?

The Face Recognition Attendance System is an AI-powered attendance management tool that uses facial recognition to automatically identify and log attendance for students and faculty members.

**Key Features:**
- ✅ Real-time face recognition
- ✅ Automatic attendance logging
- ✅ Student and Faculty management
- ✅ WhatsApp notifications for absentees
- ✅ Automated salary calculations
- ✅ Export to CSV for reporting

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or Windows 11
- **RAM**: 4GB
- **Disk Space**: 2GB free space
- **Camera**: Any webcam (built-in or USB)
- **Display**: 1280x720 or higher

### Recommended Requirements
- **RAM**: 8GB or more
- **Processor**: Intel Core i5 or equivalent
- **Camera**: HD webcam (720p or 1080p)
- **Internet**: For WhatsApp notifications (optional)

---

## Installation

### Step 1: Extract Files
1. Download the FaceAttendanceSystem_Package.zip
2. Extract all files to a folder on your computer
3. **Important**: Keep all files together in the same folder

### Step 2: First Launch
1. Navigate to the extracted folder
2. Double-click `FaceAttendanceSystem.exe`
3. Wait 10-15 seconds for the application to load
4. The login screen will appear

### No Installation Required!
- No Python installation needed
- No additional software required
- All AI models are included
- Just extract and run!

---

## First Run

### Initial Loading
The first time you run the application:
- **Loading Time**: 10-15 seconds
- **What's Happening**: Loading AI models into memory
- **Subsequent Runs**: 5-8 seconds

### Login Screen
You'll see a login screen with:
- **Username** field
- **Password** field
- **LOGIN** button

### Default Credentials

**Admin Access** (Full features):
```
Username: admin
Password: admin123
```

**User Access** (Limited features):
```
Username: user
Password: user123
```

⚠️ **Security Note**: Change these passwords after first login!

---

## User Registration

### Registering Your First User

#### Step 1: Login as Admin
1. Use admin credentials (admin/admin123)
2. Click LOGIN

#### Step 2: Start Registration
1. Click the **"Register New User"** button
2. Select user type:
   - **Student**: For students
   - **Faculty**: For staff/teachers

#### Step 3: Fill Information

**For Students:**
- Full Name (required)
- Phone Number (format: +CountryCodeNumber, e.g., +14155552671)
- Father's Name (required)
- Registration Number (required)
- Department (select from dropdown)
- Address (optional)

**For Faculty:**
- Full Name (required)
- Phone Number (format: +CountryCodeNumber)
- Designation (e.g., Professor, Lecturer)
- Department (select from dropdown)
- Salary Type:
  - **Regular/Permanent**: Fixed monthly salary
  - **Visiting**: Fixed rate or per-day rate

#### Step 4: Save Details
1. Click **"Save Details & Proceed"**
2. The face capture window will open

#### Step 5: Capture Face Images
**Important**: This step captures 80 images of your face

**Best Practices:**
- ✅ Good, even lighting
- ✅ Clean background
- ✅ Face directly at camera
- ✅ Remove glasses (if possible)
- ✅ Neutral expression
- ✅ Follow on-screen instructions

**Instructions Will Appear:**
1. Look STRAIGHT (images 1-15)
2. Look slightly UP (images 16-30)
3. Look slightly DOWN (images 31-45)
4. Turn head LEFT (images 46-60)
5. Turn head RIGHT (images 61-80)

**Tips:**
- Stay 2-3 feet from camera
- Don't move too fast
- System will tell you if image is blurry
- Green box = capturing
- Yellow box = need better position
- Red box = no face detected

#### Step 6: Processing
After capturing all 80 images:
- Wait 30-60 seconds for processing
- System builds AI model of the face
- Success message will appear
- You're done!

---

## Attendance Marking

### Automatic Recognition

#### How It Works
1. Stand in front of the camera
2. System automatically detects your face
3. Your name appears with a colored box:
   - **Blue Box**: Analyzing...
   - **Yellow Box**: Identifying... (X/4 frames)
   - **Green Box**: Recognized! Ready to mark
   - **Red Box**: Unknown person

#### Manual Marking
1. Wait for your name to appear
2. System needs 4 stable frames (about 3 seconds)
3. Box turns green when ready
4. Click **"Mark Attendance"** button
5. Your attendance is logged!

### Attendance Cooldown
- After marking, there's a 5-minute cooldown
- This prevents duplicate entries
- Status shows remaining cooldown time

### Viewing Attendance
- Check the log box at the bottom of the screen
- Shows real-time attendance entries
- Timestamp for each entry

---

## Admin Features

### 1. View All Users

**Access**: Click **"Manage Users"** button

**Features:**
- List of all registered users
- Double-click a name to see details
- View registered face samples
- See all user information

### 2. Delete Users

**How to Delete:**
1. Click **"Manage Users"**
2. Select a user from the list
3. Click **"Delete Selected User"**
4. Confirm deletion
5. Face database rebuilds automatically

⚠️ **Warning**: Deletion is permanent!

### 3. View Attendance Logs

**Student Attendance:**
1. Click **"Manage Users"**
2. Click **"View Student Log"**
3. See all student attendance entries
4. Sorted by date and time

**Faculty Attendance:**
1. Click **"Manage Users"**
2. Click **"View Faculty Log"**
3. See all faculty attendance entries

**Export to CSV:**
- CSV files are automatically created
- Location: `C:\Users\<YourName>\AppData\Local\FaceAttendanceSystem\`
- Files:
  - `student_attendance.csv`
  - `faculty_attendance.csv`

### 4. Alert Absentees (WhatsApp)

**Setup Required:**
1. Take a screenshot of WhatsApp send button (paper plane icon)
2. Crop to just the button
3. Save as `send_button.png` in application folder

**How to Send Alerts:**
1. Click **"Manage Users"**
2. Click **"Alert Absentees"**
3. See list of today's absent users
4. Select a person
5. Click **"Send Alert to Selected"**
6. Confirm the message
7. System opens WhatsApp Web automatically
8. Message sends automatically (or manually if automation fails)

**Requirements:**
- Microsoft Edge browser
- Logged into WhatsApp Web
- Active internet connection
- Display scaling at 100% (recommended)

### 5. Calculate Faculty Salaries

**How to Calculate:**
1. Click **"Manage Users"**
2. Click **"Calculate Faculty Salaries"**
3. Enter date range (From and To dates)
4. Click **"Calculate Salaries"**

**Calculation Methods:**

**Regular/Permanent Faculty:**
```
Base Salary: Monthly salary amount
Deduction: Per-day rate × absent days (if >2 absences)
Final Salary: Base Salary - Deduction
```

**Visiting Faculty:**
- **Fixed Rate**: Full amount if period ≥ 30 days
- **Per Day Rate**: Rate × present days

**Export Results:**
1. Click **"Export to CSV"** after calculation
2. File saved as `salary.csv`
3. Location: AppData folder

---

## Troubleshooting

### Application Won't Start

**Problem**: Double-clicking .exe does nothing

**Solutions:**
1. Run as Administrator:
   - Right-click FaceAttendanceSystem.exe
   - Select "Run as administrator"

2. Check Windows Defender:
   - Windows might block unknown apps
   - Click "More info" → "Run anyway"

3. Check antivirus:
   - Temporarily disable antivirus
   - Add exception for the application

### Camera Not Working

**Problem**: Black screen or "Camera not found"

**Solutions:**
1. Check camera permissions:
   - Windows Settings → Privacy → Camera
   - Enable "Allow apps to access your camera"

2. Close other apps using camera:
   - Skype, Teams, Zoom, etc.
   - Only one app can use camera at a time

3. Try different camera:
   - If you have multiple cameras
   - Unplug external cameras

4. Restart computer:
   - Sometimes helps reset camera drivers

### Face Not Recognized

**Problem**: Shows "Unknown" even for registered users

**Solutions:**
1. Check lighting:
   - Need good, even lighting
   - Avoid backlighting
   - Face camera lights

2. Check position:
   - 2-3 feet from camera
   - Face directly at camera
   - Remove glasses if worn during registration

3. Re-register:
   - Delete old registration
   - Register again with better conditions

4. Check confidence:
   - System needs 4 stable frames
   - Stand still for 3-4 seconds

### Slow Performance

**Problem**: Application is laggy or slow

**Solutions:**
1. Close other applications:
   - Especially memory-intensive apps
   - Free up RAM

2. Restart application:
   - First launch always slower
   - Subsequent launches faster

3. Check system resources:
   - Task Manager → Performance
   - Ensure enough free RAM

### WhatsApp Automation Fails

**Problem**: Message doesn't send automatically

**Solutions:**
1. Check send_button.png:
   - Must be clear screenshot
   - Only the send button
   - No extra background

2. Display scaling:
   - Windows Settings → Display
   - Set to 100% scaling
   - Restart application

3. Login to WhatsApp Web:
   - Open Edge browser
   - Go to web.whatsapp.com
   - Scan QR code to login

4. Manual sending:
   - If automation fails
   - Chat window stays open
   - Send manually

### Display Scaling Issues

**Problem**: Needle exceeds haystack error

**Solution:**
1. Windows Settings → System → Display
2. Set "Change the size of text" to 100%
3. Restart the application

**Alternative:**
- Right-click FaceAttendanceSystem.exe
- Properties → Compatibility
- Check "Override high DPI scaling behavior"
- Select "System" from dropdown

---

## FAQ

### General Questions

**Q: Do I need internet?**
A: No, except for WhatsApp notifications. All face recognition works offline.

**Q: Where is my data stored?**
A: `C:\Users\<YourName>\AppData\Local\FaceAttendanceSystem\`

**Q: Can I backup my data?**
A: Yes! Copy the entire AppData folder mentioned above.

**Q: How many users can I register?**
A: Unlimited. Performance may vary with 100+ users.

**Q: Can I use on multiple computers?**
A: Yes, but each needs separate installation and registration.

### Registration Questions

**Q: How long does registration take?**
A: 2-3 minutes per person (80 images + processing).

**Q: Can I register with glasses?**
A: Yes, but recognition works better without.

**Q: What if I change hairstyle?**
A: Re-register if appearance changes significantly.

**Q: Can I register multiple people at once?**
A: No, one at a time for best accuracy.

### Recognition Questions

**Q: How accurate is the recognition?**
A: 95%+ accuracy with good lighting and quality images.

**Q: How fast is recognition?**
A: 1-3 seconds per face detection.

**Q: Can it recognize multiple people?**
A: Yes, but processes one face at a time (largest face first).

**Q: What's the recognition range?**
A: 2-6 feet from camera works best.

### Data Questions

**Q: Can I export data?**
A: Yes, attendance and salary data export to CSV.

**Q: Can I edit CSV files?**
A: Yes, open with Excel or any spreadsheet program.

**Q: How long is data kept?**
A: Forever, unless you manually delete CSV files.

**Q: Can I import old data?**
A: Not directly, but you can edit CSV files.

---

## Data Backup

### What to Backup

**Critical Data:**
- `face_database/` - All registered face images
- `student_attendance.csv` - Student logs
- `faculty_attendance.csv` - Faculty logs
- `salary.csv` - Salary calculations

**Backup Location:**
```
C:\Users\<YourName>\AppData\Local\FaceAttendanceSystem\
```

### How to Backup

1. Open File Explorer
2. Type in address bar: `%LOCALAPPDATA%\FaceAttendanceSystem`
3. Copy entire folder to external drive or cloud
4. Create dated backup: `FaceAttendanceSystem_Backup_2024-11-13`

### How to Restore

1. Close the application
2. Go to backup folder
3. Copy contents to: `%LOCALAPPDATA%\FaceAttendanceSystem`
4. Replace when prompted
5. Start application

---

## Support

### Getting Help

1. **Check this guide first**
2. **Check validation_log.json** for technical details
3. **Visit**: https://github.com/DaniyalFaheem/Face
4. **Create Issue**: Describe problem + attach validation_log.json

### Reporting Bugs

Include:
- What you were doing
- Error message (if any)
- Screenshot of problem
- validation_log.json file
- Windows version

---

## Credits

**Developers**: DaniyalFaheem
**AI Framework**: DeepFace (Facebook Research)
**ML Backend**: TensorFlow (Google)
**Computer Vision**: OpenCV

**Version**: 1.0.0
**Release Date**: November 2024
**License**: See LICENSE.txt

---

**Thank you for using Face Recognition Attendance System!**

For the latest updates and support, visit:
https://github.com/DaniyalFaheem/Face
