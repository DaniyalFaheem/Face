# =================================================================================================
# ENVIRONMENT REQUIREMENT
# =================================================================================================
# This script is designed to run on PYTHON 3.8.x.
# The error 'TypeError: unhashable type: 'list'' occurs due to an incompatibility
# between TensorFlow (a dependency of DeepFace) and Python 3.9+.
#
# To set up the correct environment:
# 1. Install Python 3.8.
# 2. Create a virtual environment: python -m venv venv
# 3. Activate it: .\venv\Scripts\activate
# 4. Install dependencies: pip install -r requirements.txt
#    (Ensure your requirements.txt specifies compatible versions of libraries like tensorflow)
# =================================================================================================

import os
# --- FIX: SUPPRESS TENSORFLOW LOGS AND DEPRECATION WARNINGS ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources.*")

# --- FIX: MAKE THE SCRIPT DPI-AWARE ON WINDOWS (Most Critical Fix) ---
# This resolves the 'needle exceeds haystack' error on systems with display scaling.
import sys
import ctypes
if sys.platform == "win32":
    try:
        # This line tells Windows that our application understands how to handle
        # different screen scaling settings. This is the most important fix.
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        print(f"INFO: Could not set DPI awareness. If screen automation fails, try setting display scaling to 100%. Error: {e}")
# --- END OF FIX ---

import cv2
import pandas as pd
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ImageFilter
from datetime import datetime, timedelta, date
import numpy as np
import threading
import time
from collections import Counter
import shutil
import queue
from concurrent.futures import ThreadPoolExecutor
import json

# --- GRACEFUL DEEPFACE IMPORT ---
try:
    from deepface import DeepFace
except ImportError as e:
    root = Tk()
    root.withdraw()
    messagebox.showerror(
        "Dependency Error",
        f"A critical library is missing or failed to import: {e}\n\n"
        "Please ensure you have set up the environment correctly using the provided 'requirements.txt' file."
    )
    sys.exit()

# --- WHATSAPP & AUTOMATION LIBRARY IMPORTS ---
try:
    import pywhatkit
    import webbrowser
    import pyautogui
    import urllib.parse
except ImportError as e:
    root = Tk()
    root.withdraw()
    messagebox.showerror(
        "Dependency Error",
        f"A required library is missing: {e}.\n\n"
        "Please ensure 'pywhatkit' and 'pyautogui' are installed."
    )
    sys.exit()

# --- Helper Class for Placeholder Entry (Fixed) ---
class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder
        self.insert("0", self.placeholder)
        
        # Determine if the entry is for a password
        self._is_password = 'show' in kwargs and kwargs['show'] == '*'
        
        # Set placeholder style initially
        self.configure(style="Placeholder.TEntry")
        if self._is_password:
             self.configure(show="")

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self.get() == self.placeholder:
            self.delete("0", "end")
            if self._is_password:
                self.configure(show='*')
            self.configure(style="TEntry")

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            if self._is_password:
                self.configure(show='')
            self.configure(style="Placeholder.TEntry")

# --- Main Face Recognition Application Class ---
class FaceRecognitionApp:
    def __init__(self, root, role="admin"):
        self.root = root
        self.role = role  # Can be "admin" or "user"
        self.root.title("Face Recognition Attendance System")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.geometry("1280x720")

        self.is_maximized = False
        self.original_geometry = ""
        self.last_x, self.last_y = 0, 0
        self.root.bind("<Escape>", self.on_closing)
        self.root.bind("<Map>", self.on_map)

        # --- UI Theming and Colors ---
        self.COLOR_PRIMARY = "#2C3E50"
        self.COLOR_SECONDARY = "#34495E"
        self.COLOR_ACCENT = "#3498DB"
        self.COLOR_SUCCESS = "#2ECC71"
        self.COLOR_WARNING = "#F1C40F"
        self.COLOR_DANGER = "#E74C3C"
        self.COLOR_TEXT_LIGHT = "#ECF0F1"
        self.COLOR_TEXT_DARK = "#2C3E50"
        self.COLOR_INPUT_BG = "#404040"
        self.root.configure(bg=self.COLOR_PRIMARY)

        self.CV_COLOR_ACCENT = self.hex_to_bgr(self.COLOR_ACCENT)
        self.CV_COLOR_SUCCESS = self.hex_to_bgr(self.COLOR_SUCCESS)
        self.CV_COLOR_WARNING = self.hex_to_bgr(self.COLOR_WARNING)
        self.CV_COLOR_DANGER = self.hex_to_bgr(self.COLOR_DANGER)
        self.CV_COLOR_TEXT_LIGHT = self.hex_to_bgr(self.COLOR_TEXT_LIGHT)

        # --- File and Path Configuration ---
        self.camera_index = 0
        self.student_attendance_file = "student_attendance.csv"
        self.faculty_attendance_file = "faculty_attendance.csv"
        self.salary_file = "salary.csv"
        self.db_path = "face_database"
        self.LOG_COOLDOWN_SECONDS = 300
        
        self.STUDENT_DEPARTMENTS = ["BSIT", "BS Cyber Security", "BBA", "BSCS", "ADP IT", "ADP Cyber Security", "Other ADP Program"]
        self.FACULTY_DEPARTMENTS = ["IT", "CS", "BBA", "Cyber Security"]

        # --- SPEED & PERFORMANCE TUNING PARAMETERS ---
        self.RECOGNITION_INTERVAL = 0.75
        self.FRAME_PROCESS_SCALE_FACTOR = 0.5
        self.DISPLAY_LOOP_MS = 15
        self.HISTORY_MAX_LENGTH = 8
        self.CONFIDENCE_THRESHOLD_PERCENT = 0.75
        self.REQUIRED_STABLE_FRAMES = 4
        self.HAAR_MIN_FACE_SIZE = (50, 50)

        # --- MODEL CONFIGURATION FOR SPEED ---
        self.DEEPFACE_MODEL = 'VGG-Face'
        self.DEEPFACE_METRIC = 'cosine'
        self.DEEPFACE_DISTANCE_THRESHOLD = 0.40
        self.DEEPFACE_DETECTOR_BACKEND = 'ssd'

        # --- State Variables ---
        self.database_ready = False
        self.locked_in_person = None
        self.recognition_history = []
        self.stable_recognition_count = 0
        self.recently_logged = {}
        self.last_recognition_result = ("Searching...", float('inf'))
        self.last_recognition_time = 0
        self.salary_data_for_export = []

        # --- Threading and Queues ---
        self.write_lock = threading.Lock()
        self.app_running = threading.Event()
        self.app_running.set()
        self.camera_thread = None
        self.processing_thread = None
        self.raw_frame_queue = queue.Queue(maxsize=2)
        self.processed_frame_queue = queue.Queue(maxsize=2)
        self.recognition_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Recognition')
        self.recognition_future = None

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
        except Exception as e:
            messagebox.showerror("OpenCV Error", f"Failed to load OpenCV components: {e}")
            self.root.destroy()
            return

        self.setup_styles()
        self.create_widgets()

    def hex_to_bgr(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))

    def run_initial_setup(self):
        self.initialize_attendance()
        self.toggle_maximize()
        threading.Thread(target=self._initialize_models_and_verify_db, daemon=True).start()
        self.start_camera()

    def setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('TFrame', background=self.COLOR_PRIMARY)
        s.configure('TLabel', background=self.COLOR_PRIMARY, foreground=self.COLOR_TEXT_LIGHT, font=("Segoe UI", 12))
        s.configure('Title.TLabel', font=("Segoe UI", 24, "bold"), foreground=self.COLOR_ACCENT)
        s.configure('Status.TLabel', font=("Segoe UI", 12, "italic"))
        s.configure('TButton', font=("Segoe UI", 12, "bold"), padding=10, relief="flat", background=self.COLOR_ACCENT, foreground=self.COLOR_TEXT_LIGHT)
        s.map('TButton', background=[('active', self.COLOR_ACCENT)], relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        s.configure('Success.TButton', background=self.COLOR_SUCCESS)
        s.map('Success.TButton', background=[('active', self.COLOR_SUCCESS)])
        s.configure('Danger.TButton', background=self.COLOR_DANGER)
        s.map('Danger.TButton', background=[('active', self.COLOR_DANGER)])
        s.configure('Warning.TButton', background=self.COLOR_WARNING, foreground=self.COLOR_TEXT_DARK)
        s.map('Warning.TButton', background=[('active', self.COLOR_WARNING)])
        s.configure('Switch.TButton', font=("Segoe UI", 12, "bold"), padding=12, background=self.COLOR_WARNING, foreground=self.COLOR_TEXT_DARK)
        s.map('Switch.TButton', background=[('active', '#F39C12')])
        s.configure("TEntry", fieldbackground=self.COLOR_INPUT_BG, foreground=self.COLOR_TEXT_LIGHT, insertcolor=self.COLOR_TEXT_LIGHT, font=("Segoe UI", 11))
        s.configure("Placeholder.TEntry", foreground="#8A8A8A")
        s.configure('TText', background=self.COLOR_INPUT_BG, foreground=self.COLOR_TEXT_LIGHT, font=("Consolas", 10))
        s.configure('Control.TButton', font=("Arial", 10), padding=5, relief="flat", background=self.COLOR_SECONDARY)
        s.map('Control.TButton', background=[('active', self.COLOR_ACCENT)])
        s.configure('Close.TButton', background=self.COLOR_DANGER)
        s.map('Close.TButton', background=[('active', self.COLOR_DANGER)])
        s.configure("Treeview", background=self.COLOR_INPUT_BG, foreground=self.COLOR_TEXT_LIGHT, fieldbackground=self.COLOR_INPUT_BG, rowheight=25, font=("Segoe UI", 10))
        s.map("Treeview", background=[('selected', self.COLOR_ACCENT)])
        s.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background=self.COLOR_SECONDARY, foreground=self.COLOR_TEXT_LIGHT)
        s.configure("TRadiobutton", background=self.COLOR_PRIMARY, foreground=self.COLOR_TEXT_LIGHT, font=("Segoe UI", 11))
        s.map("TRadiobutton", background=[('active', self.COLOR_SECONDARY)])

    def create_widgets(self):
        control_frame = Frame(self.root, bg=self.COLOR_SECONDARY, height=40)
        control_frame.pack(fill=X, side=TOP)
        control_frame.grid_columnconfigure(0, weight=1)

        title_text = "Face Recognition Attendance System"
        if self.role == "admin": title_text += " [ADMIN PANEL]"
        elif self.role == "user": title_text += " [USER PANEL]"
        Label(control_frame, text=title_text, font=("Segoe UI", 14, "bold"), bg=self.COLOR_SECONDARY, fg=self.COLOR_TEXT_LIGHT).grid(row=0, column=0, sticky="w", padx=10)

        self.minimize_btn = ttk.Button(control_frame, text="—", command=self.minimize_window, style='Control.TButton', width=3); self.minimize_btn.grid(row=0, column=1)
        self.maximize_btn = ttk.Button(control_frame, text="☐", command=self.toggle_maximize, style='Control.TButton', width=3); self.maximize_btn.grid(row=0, column=2)
        self.close_btn = ttk.Button(control_frame, text="✕", command=self.on_closing, style='Close.TButton', width=3); self.close_btn.grid(row=0, column=3, padx=(0, 5))
        control_frame.bind("<ButtonPress-1>", self.start_move); control_frame.bind("<B1-Motion>", self.do_move)
        
        ttk.Label(self.root, text="📷 Attendance System", style='Title.TLabel').pack(pady=(0,5))
        
        video_width, video_height = 960, 540
        self.video_label = Label(self.root, bg=self.COLOR_SECONDARY, relief="solid", bd=2); self.video_label.pack(pady=5)
        placeholder_img = Image.new('RGB', (video_width, video_height), self.COLOR_SECONDARY)
        self._placeholder_imgtk = ImageTk.PhotoImage(image=placeholder_img)
        self.video_label.configure(image=self._placeholder_imgtk, width=video_width, height=video_height)
        
        self.status_label = ttk.Label(self.root, text="Status: Initializing...", style='Status.TLabel'); self.status_label.pack(pady=(5, 5))
        
        button_frame = ttk.Frame(self.root); button_frame.pack(pady=5)
        
        self.mark_attendance_btn = ttk.Button(button_frame, text="✅ Mark Attendance", command=self.manual_mark_attendance, style='Success.TButton', state=DISABLED); self.mark_attendance_btn.grid(row=0, column=0, padx=10)
        
        if self.role == "admin":
            ttk.Button(button_frame, text="➕ Register New User", command=self.register_face, style='Warning.TButton').grid(row=0, column=1, padx=10)
            ttk.Button(button_frame, text="🗑 Clear Log", command=self.clear_log, style='Danger.TButton').grid(row=0, column=2, padx=10)
            ttk.Button(button_frame, text="📊 Manage Users", command=self.show_stats, style='TButton').grid(row=0, column=3, padx=10)
        else: 
            ttk.Button(button_frame, text="➕ Register Student", command=self.register_face, style='Warning.TButton').grid(row=0, column=1, padx=10)
            ttk.Button(button_frame, text="📊 View Students", command=self.show_stats, style='TButton').grid(row=0, column=2, padx=10)

        self.attendance_box = Text(self.root, height=5, font=("Consolas", 10), bg=self.COLOR_INPUT_BG, fg=self.COLOR_TEXT_LIGHT, relief="solid", bd=1); self.attendance_box.pack(pady=(10,0), fill=X, padx=20); self.attendance_box.config(state=DISABLED)
        
        bottom_bar = ttk.Frame(self.root, style='TFrame'); bottom_bar.pack(side=BOTTOM, fill=X, padx=10, pady=(5,10))
        ttk.Button(bottom_bar, text="🔑 Switch", command=self.switch_panel, style='Switch.TButton').pack(side=LEFT, padx=10)

    def switch_panel(self):
        self.stop_all_threads()
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.withdraw()
        login()

    def start_move(self, event): self.last_x, self.last_y = event.x_root, event.y_root
    
    def do_move(self, event):
        if not self.is_maximized:
            self.root.geometry(f"+{self.root.winfo_x() + event.x_root - self.last_x}+{self.root.winfo_y() + event.y_root - self.last_y}")
            self.last_x, self.last_y = event.x_root, event.y_root

    def minimize_window(self):
        self.root.overrideredirect(False)
        self.root.iconify()

    def on_map(self, event):
        self.root.after(10, self.root.overrideredirect, True)

    def toggle_maximize(self):
        if not self.is_maximized:
            self.original_geometry = self.root.geometry()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.maximize_btn.config(text="🗗")
        else: 
            self.root.geometry(self.original_geometry)
            self.maximize_btn.config(text="☐")
        self.is_maximized = not self.is_maximized

    def on_closing(self, event=None):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"): 
            self.stop_all_threads()
            self.root.destroy()

    def stop_all_threads(self):
        self.log_message("System shutting down...")
        self.app_running.clear()
        if self.recognition_executor: self.recognition_executor.shutdown(wait=False, cancel_futures=True)
        if self.camera_thread and self.camera_thread.is_alive(): self.camera_thread.join(timeout=1.0)
        if self.processing_thread and self.processing_thread.is_alive(): self.processing_thread.join(timeout=1.0)
        self.log_message("Shutdown complete.")

    def manual_mark_attendance(self):
        if self.locked_in_person: self.mark_attendance(self.locked_in_person)
        else: messagebox.showwarning("Attendance Error", "No person recognized to mark attendance.")

    def initialize_attendance(self):
        try:
            if not os.path.exists(self.student_attendance_file):
                pd.DataFrame(columns=["Name", "Department", "Date", "Time"]).to_csv(self.student_attendance_file, index=False)
            if not os.path.exists(self.faculty_attendance_file):
                pd.DataFrame(columns=["Name", "Department", "Date", "Time"]).to_csv(self.faculty_attendance_file, index=False)
        except Exception as e:
            self.log_message(f"Error initializing attendance files: {e}")
            messagebox.showerror("File Error", f"Could not initialize attendance files:\n{e}")

    def _initialize_models_and_verify_db(self):
        """
        Handles the loading of DeepFace models and verifies the database.
        This is a blocking call and should be run in a separate thread.
        """
        if self.root.winfo_exists():
            self.root.after(0, self._update_status, "Status: Checking face database...", self.COLOR_WARNING)

        if not os.path.exists(self.db_path) or not os.listdir(self.db_path):
            if self.root.winfo_exists(): self.root.after(0, self._update_status, "Status: Database empty. Please register users.", self.COLOR_DANGER)
            self.log_message("Warning: Face database is empty.")
            self.database_ready = False
            return

        user_folders = [d for d in os.listdir(self.db_path) if os.path.isdir(os.path.join(self.db_path, d))]
        if not user_folders:
            if self.root.winfo_exists(): self.root.after(0, self._update_status, "Status: Database empty. Please register users.", self.COLOR_DANGER)
            self.log_message("Warning: Face database contains no user folders.")
            self.database_ready = False
            return

        try:
            self.log_message(f"Loading '{self.DEEPFACE_MODEL}' model... This may take a moment.")
            if self.root.winfo_exists(): self.root.after(0, self._update_status, "Status: Loading face recognition models...", self.COLOR_WARNING)

            blank_image = np.zeros((100, 100, 3), dtype=np.uint8)
            DeepFace.find(
                img_path=blank_image,
                db_path=self.db_path,
                model_name=self.DEEPFACE_MODEL,
                detector_backend=self.DEEPFACE_DETECTOR_BACKEND,
                enforce_detection=False,
                silent=True
            )
            self.database_ready = True
            if self.root.winfo_exists(): self.root.after(0, self._update_status, "Status: Ready for live recognition.", self.COLOR_SUCCESS)
            self.log_message(f"Database check passed. Found {len(user_folders)} users.")

        except Exception as e:
            error_message = f"Could not initialize face recognition models: {e}"
            self.log_message(f"CRITICAL: DeepFace model initialization failed. Error: {e}")
            self.log_message("This can be caused by corrupted model files, dependency issues (TensorFlow, OpenCV), or an invalid database structure.")
            
            if self.root.winfo_exists():
                self.root.after(0, self._update_status, "Status: Error loading DeepFace models.", self.COLOR_DANGER)
                messagebox.showerror("Model Loading Failed", error_message)
            self.database_ready = False
    
    def start_camera(self):
        self.stop_camera()
        self.app_running.set()
        self.camera_thread = threading.Thread(target=self._camera_capture_worker, daemon=True)
        self.camera_thread.start()
        self.processing_thread = threading.Thread(target=self._frame_processing_worker, daemon=True)
        self.processing_thread.start()
        self.root.after(100, self._display_loop)
        self.log_message("Camera started.")

    def stop_camera(self):
        self.app_running.clear()
        if self.camera_thread and self.camera_thread.is_alive(): self.camera_thread.join(timeout=0.5)
        if self.processing_thread and self.processing_thread.is_alive(): self.processing_thread.join(timeout=0.5)
        for q in [self.raw_frame_queue, self.processed_frame_queue]:
            while not q.empty():
                try: q.get_nowait()
                except queue.Empty: pass

    def _camera_capture_worker(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            if self.root.winfo_exists(): self.root.after(0, self._update_status, f"Status: Camera {self.camera_index} not found!", self.COLOR_DANGER)
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480); cap.set(cv2.CAP_PROP_FPS, 30); cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        while self.app_running.is_set():
            ret, frame = cap.read()
            if not ret: time.sleep(0.01); continue
            try: self.raw_frame_queue.put(frame, block=False)
            except queue.Full: pass
        cap.release()

    def _frame_processing_worker(self):
        while self.app_running.is_set():
            try:
                frame = self.raw_frame_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            
            frame = cv2.flip(frame, 1)
            small_frame = cv2.resize(frame, (0, 0), fx=self.FRAME_PROCESS_SCALE_FACTOR, fy=self.FRAME_PROCESS_SCALE_FACTOR, interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=self.HAAR_MIN_FACE_SIZE)
            
            face_coords = None
            if len(faces) > 0:
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                x, y, w, h = (int(c / self.FRAME_PROCESS_SCALE_FACTOR) for c in largest_face)
                face_coords = (x, y, w, h)

            current_time = time.monotonic()
            is_recognition_running = self.recognition_future and self.recognition_future.running()
            
            if self.database_ready and face_coords and not is_recognition_running and (current_time - self.last_recognition_time > self.RECOGNITION_INTERVAL):
                self.last_recognition_time = current_time
                self.recognition_future = self.recognition_executor.submit(self._run_deepface_recognition, frame.copy())
            
            self.update_recognition_state(self.last_recognition_result[0])
            annotated_frame = self.draw_on_frame(frame, face_coords, self.last_recognition_result[0], self.last_recognition_result[1])
            
            try:
                self.processed_frame_queue.put(annotated_frame, block=False)
            except queue.Full:
                pass

    def _run_deepface_recognition(self, frame):
        try:
            dfs = DeepFace.find(img_path=frame, db_path=self.db_path, model_name=self.DEEPFACE_MODEL, distance_metric=self.DEEPFACE_METRIC, enforce_detection=False, detector_backend=self.DEEPFACE_DETECTOR_BACKEND, silent=True)
            if isinstance(dfs, list) and len(dfs) > 0 and not dfs[0].empty:
                df = dfs[0]
                best_match = df.iloc[0]
                distance = best_match['distance']
                if distance < self.DEEPFACE_DISTANCE_THRESHOLD:
                    identity_path = best_match['identity']
                    name = os.path.basename(os.path.dirname(identity_path)).replace('_', ' ')
                    self.last_recognition_result = (name, distance)
                else:
                    self.last_recognition_result = ("Unknown", distance)
            else:
                self.last_recognition_result = ("Unknown", float('inf'))
        except Exception:
            self.last_recognition_result = ("Unknown", float('inf'))

    def _display_loop(self):
        if not self.app_running.is_set():
            if self.root.winfo_exists(): self.video_label.configure(image=self._placeholder_imgtk)
            return
        try:
            annotated_frame = self.processed_frame_queue.get_nowait()
            img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            if self.root.winfo_exists(): 
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(self.DISPLAY_LOOP_MS, self._display_loop)

    def update_recognition_state(self, name):
        self.recognition_history.append(name)
        if len(self.recognition_history) > self.HISTORY_MAX_LENGTH:
            self.recognition_history.pop(0)

        if not self.recognition_history: return

        most_common_name, count = Counter(self.recognition_history).most_common(1)[0]
        proportion = count / len(self.recognition_history)

        if (most_common_name not in ["Unknown", "Error", "Searching..."] and proportion >= self.CONFIDENCE_THRESHOLD_PERCENT):
            if self.stable_recognition_count < self.REQUIRED_STABLE_FRAMES:
                self.stable_recognition_count += 1
            else:
                if self.locked_in_person != most_common_name:
                    self.locked_in_person = most_common_name
                    if self.root.winfo_exists(): self.root.after(0, self.mark_attendance_btn.config, {'state': NORMAL})
        else:
            self.stable_recognition_count = 0
            if self.locked_in_person:
                 self.locked_in_person = None
                 self.recognition_history.clear()
                 if self.root.winfo_exists(): self.root.after(0, self.mark_attendance_btn.config, {'state': DISABLED})

    def draw_on_frame(self, frame, face_coords, name, distance):
        status_text, status_color_hex = "Status: Searching for a face...", self.COLOR_ACCENT
        box_color_bgr, display_name = self.CV_COLOR_ACCENT, "Searching..."

        if self.locked_in_person:
            is_on_cooldown = self.locked_in_person in self.recently_logged and datetime.now() < self.recently_logged[self.locked_in_person]
            if is_on_cooldown:
                remaining = int((self.recently_logged[self.locked_in_person] - datetime.now()).total_seconds())
                status_text, status_color_hex = f"Status: {self.locked_in_person} already logged. Cooldown: {remaining}s", self.COLOR_WARNING
                box_color_bgr = self.CV_COLOR_WARNING
            else:
                status_text, status_color_hex = f"Status: Recognized: {self.locked_in_person}. Ready to Mark.", self.COLOR_SUCCESS
                box_color_bgr = self.CV_COLOR_SUCCESS
            display_name = self.locked_in_person
        elif self.stable_recognition_count > 0 and name not in ["Searching...", "Unknown"]:
            status_text, status_color_hex = f"Status: Identifying {name}... ({self.stable_recognition_count}/{self.REQUIRED_STABLE_FRAMES})", self.COLOR_WARNING
            box_color_bgr = self.CV_COLOR_WARNING; display_name = name
        elif face_coords:
            if name == "Unknown":
                status_text, status_color_hex, display_name = "Status: Unknown face detected. Please register.", self.COLOR_DANGER, "Unknown"
                box_color_bgr = self.CV_COLOR_DANGER
            else:
                status_text, display_name = "Status: Analyzing face...", "Analyzing..."
                box_color_bgr = self.CV_COLOR_ACCENT
        
        if face_coords:
            x, y, w, h = face_coords
            cv2.rectangle(frame, (x, y), (x+w, y+h), box_color_bgr, 2)
            text = f"{display_name} (Dist: {distance:.2f})" if distance != float('inf') else display_name
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x, y - text_h - 15), (x + w, y - 10), box_color_bgr, -1)
            cv2.putText(frame, text, (x + 5, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.CV_COLOR_TEXT_LIGHT, 2)

        if self.root.winfo_exists(): self.root.after(0, self._update_status, status_text, status_color_hex)
        return cv2.resize(frame, (960, 540), interpolation=cv2.INTER_AREA)

    def _update_status(self, text, hex_color):
        if self.root.winfo_exists() and self.status_label.winfo_exists():
            if self.status_label.cget('text') != text: self.status_label.config(text=text, foreground=hex_color)

    def register_face(self):
        self.stop_camera()
        if self.role == "user": 
            self._show_registration_form('Student')
            return
            
        type_win = Toplevel(self.root); type_win.title("Select User Type"); type_win.configure(bg=self.COLOR_PRIMARY)
        type_win.resizable(False, False); type_win.transient(self.root); type_win.grab_set()
        
        self.root.update_idletasks()
        win_w, win_h = 350, 200
        x = self.root.winfo_x() + (self.root.winfo_width() - win_w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - win_h) // 2
        type_win.geometry(f'{win_w}x{win_h}+{x}+{y}')

        def select_type(user_type): 
            type_win.destroy()
            self._show_registration_form(user_type)
        
        def on_cancel(): 
            type_win.destroy()
            self.start_camera()

        ttk.Label(type_win, text="Who are you registering?", font=("Segoe UI", 14, "bold")).pack(pady=20)
        btn_frame = ttk.Frame(type_win); btn_frame.pack(pady=10, fill=X, expand=True)
        ttk.Button(btn_frame, text="🎓 Student", command=lambda: select_type('Student')).pack(side=LEFT, expand=True, padx=10)
        ttk.Button(btn_frame, text="💼 Faculty", command=lambda: select_type('Faculty')).pack(side=RIGHT, expand=True, padx=10)
        type_win.protocol("WM_DELETE_WINDOW", on_cancel)

    def _show_registration_form(self, user_type):
        form_win = Toplevel(self.root)
        form_win.title(f"Register New {user_type}")
        form_win.configure(bg=self.COLOR_PRIMARY)
        form_win.resizable(False, False); form_win.transient(self.root); form_win.grab_set()
        
        form_frame = ttk.Frame(form_win, padding="20"); form_frame.pack(expand=True, fill=BOTH)
        widgets = {}; row_idx = 0
        
        ttk.Label(form_frame, text=f"{user_type} Name:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
        widgets['name'] = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11)); widgets['name'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1
        
        ttk.Label(form_frame, text="Phone Number:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
        widgets['phone_number'] = PlaceholderEntry(form_frame, "+CountryCodeNumber (e.g., +14155552671)", width=40, font=("Segoe UI", 11));
        widgets['phone_number'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1

        if user_type == 'Student':
            ttk.Label(form_frame, text="Father's Name:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
            widgets['father_name'] = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11)); widgets['father_name'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1
            
            ttk.Label(form_frame, text="Registration No:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
            widgets['reg_no'] = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11)); widgets['reg_no'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1
            
            ttk.Label(form_frame, text="Department:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
            widgets['department'] = ttk.Combobox(form_frame, values=self.STUDENT_DEPARTMENTS, state="readonly", width=38, font=("Segoe UI", 11)); widgets['department'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1
            widgets['department'].set("Select Department")

            ttk.Label(form_frame, text="Address:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
            widgets['address'] = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11)); widgets['address'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1

        elif user_type == 'Faculty':
            ttk.Label(form_frame, text="Designation:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
            widgets['designation'] = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11)); widgets['designation'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1
            
            ttk.Label(form_frame, text="Department:", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5)
            widgets['department'] = ttk.Combobox(form_frame, values=self.FACULTY_DEPARTMENTS, state="readonly", width=38, font=("Segoe UI", 11)); widgets['department'].grid(row=row_idx, column=1, pady=5, padx=5); row_idx += 1
            widgets['department'].set("Select Department")
            
            ttk.Separator(form_frame).grid(row=row_idx, columnspan=2, sticky="ew", pady=10); row_idx += 1
            ttk.Label(form_frame, text="Salary Details", font=("Segoe UI", 11, "bold")).grid(row=row_idx, column=0, sticky="w", pady=5); row_idx += 1

            salary_type_var = StringVar(value="None")
            widgets['salary_type'] = salary_type_var
            
            salary_frame = ttk.Frame(form_frame); salary_frame.grid(row=row_idx, column=0, columnspan=2, sticky='w'); row_idx += 1
            ttk.Radiobutton(salary_frame, text="Regular / Permanent", variable=salary_type_var, value="Regular").pack(side=LEFT, padx=5)
            ttk.Radiobutton(salary_frame, text="Visiting", variable=salary_type_var, value="Visiting").pack(side=LEFT, padx=20)

            salary_details_frame = ttk.Frame(form_frame); salary_details_frame.grid(row=row_idx, column=0, columnspan=2, pady=5); row_idx +=1
            
            def update_salary_fields(*args):
                for widget in salary_details_frame.winfo_children(): widget.destroy()
                
                widgets.pop('monthly_salary', None); widgets.pop('visiting_type', None); widgets.pop('visiting_rate', None)

                sel_type = salary_type_var.get()
                if sel_type == "Regular":
                    ttk.Label(salary_details_frame, text="Monthly Salary:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", padx=5)
                    widgets['monthly_salary'] = ttk.Entry(salary_details_frame, width=20, font=("Segoe UI", 11)); widgets['monthly_salary'].grid(row=0, column=1, sticky="w", padx=5)
                
                elif sel_type == "Visiting":
                    visiting_type_var = StringVar(value="None")
                    widgets['visiting_type'] = visiting_type_var
                    
                    visiting_frame = ttk.Frame(salary_details_frame); visiting_frame.grid(row=0, column=0, columnspan=2, sticky='w')
                    ttk.Radiobutton(visiting_frame, text="Fixed Rate (30 days)", variable=visiting_type_var, value="Fixed").pack(side=LEFT, padx=5)
                    ttk.Radiobutton(visiting_frame, text="Per Day Rate", variable=visiting_type_var, value="PerDay").pack(side=LEFT, padx=5)

                    visiting_rate_frame = ttk.Frame(salary_details_frame); visiting_rate_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=5)
                    
                    def update_visiting_rate_field(*args):
                        for widget in visiting_rate_frame.winfo_children(): widget.destroy()
                        widgets.pop('visiting_rate', None)
                        
                        visit_sel = visiting_type_var.get()
                        if visit_sel in ["Fixed", "PerDay"]:
                            label_text = "Fixed Amount:" if visit_sel == "Fixed" else "Per Day Amount:"
                            ttk.Label(visiting_rate_frame, text=label_text, font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", padx=5)
                            widgets['visiting_rate'] = ttk.Entry(visiting_rate_frame, width=20, font=("Segoe UI", 11)); widgets['visiting_rate'].grid(row=0, column=1, sticky="w", padx=5)

                    visiting_type_var.trace("w", update_visiting_rate_field)
            
            salary_type_var.trace("w", update_salary_fields)

        submit_btn = ttk.Button(form_frame, text="Save Details & Proceed", style="Success.TButton", command=lambda: self._process_registration(form_win, user_type, widgets))
        submit_btn.grid(row=row_idx, column=0, columnspan=2, pady=20)
        def on_cancel(): form_win.destroy(); self.start_camera()
        form_win.protocol("WM_DELETE_WINDOW", on_cancel)

    def _process_registration(self, form_win, user_type, widgets):
        details = {'user_type': user_type}
        
        name = widgets['name'].get().strip()
        if not name or not name.replace('_', '').replace(' ', '').isalnum():
            messagebox.showerror("Invalid Input", "Name is required and must be alphanumeric.", parent=form_win)
            return
        details['name'] = name

        phone_widget = widgets['phone_number']
        phone_number = phone_widget.get().strip()
        if phone_number == phone_widget.placeholder or not phone_number:
            messagebox.showerror("Invalid Input", "Phone Number is required.", parent=form_win)
            return
        if not (phone_number.startswith('+') and phone_number[1:].isdigit()):
            messagebox.showerror("Invalid Input", "Phone number must be in the format +CountryCodeNumber (e.g., +14155552671).", parent=form_win)
            return
        details['phone_number'] = phone_number

        if user_type == 'Student':
            father_name = widgets['father_name'].get().strip()
            if not father_name:
                messagebox.showerror("Invalid Input", "Father's Name is required.", parent=form_win); return
            details['father_name'] = father_name

            reg_no = widgets['reg_no'].get().strip()
            if not reg_no:
                messagebox.showerror("Invalid Input", "Registration Number is required.", parent=form_win); return
            details['reg_no'] = reg_no
            
            department = widgets['department'].get()
            if department == "Select Department":
                messagebox.showerror("Invalid Input", "Department is required.", parent=form_win); return
            details['department'] = department
            details['address'] = widgets['address'].get().strip()

        elif user_type == 'Faculty':
            designation = widgets['designation'].get().strip()
            if not designation:
                messagebox.showerror("Invalid Input", "Designation is required.", parent=form_win); return
            details['designation'] = designation

            department = widgets['department'].get()
            if department == "Select Department":
                messagebox.showerror("Invalid Input", "Department is required.", parent=form_win); return
            details['department'] = department

            salary_type = widgets['salary_type'].get()
            if salary_type == "None":
                messagebox.showerror("Invalid Input", "Salary Type (Regular or Visiting) is required.", parent=form_win); return
            details['salary_type'] = salary_type

            if salary_type == "Regular":
                monthly_salary_str = widgets.get('monthly_salary').get().strip() if widgets.get('monthly_salary') else ""
                if not monthly_salary_str:
                    messagebox.showerror("Invalid Input", "Monthly Salary is required for Regular faculty.", parent=form_win); return
                try:
                    if float(monthly_salary_str) < 0:
                        messagebox.showerror("Invalid Input", "Monthly Salary cannot be negative.", parent=form_win); return
                except ValueError:
                    messagebox.showerror("Invalid Input", "Monthly Salary must be a valid number.", parent=form_win); return
                details['monthly_salary'] = monthly_salary_str

            elif salary_type == "Visiting":
                visiting_type = widgets['visiting_type'].get()
                if visiting_type == "None":
                    messagebox.showerror("Invalid Input", "Visiting Type (Fixed or Per Day) is required.", parent=form_win); return
                details['visiting_type'] = visiting_type
                
                visiting_rate_str = widgets.get('visiting_rate').get().strip() if widgets.get('visiting_rate') else ""
                if not visiting_rate_str:
                    messagebox.showerror("Invalid Input", "A salary rate is required for Visiting faculty.", parent=form_win); return
                try:
                    if float(visiting_rate_str) < 0:
                        messagebox.showerror("Invalid Input", "Visiting Rate cannot be negative.", parent=form_win); return
                except ValueError:
                    messagebox.showerror("Invalid Input", "Visiting Rate must be a valid number.", parent=form_win); return
                details['visiting_rate'] = visiting_rate_str

        folder_name = name.replace(' ', '_')
        user_path = os.path.join(self.db_path, folder_name)
        if os.path.exists(user_path):
            if not messagebox.askyesno("User Exists", f"'{name}' already exists. Overwrite their data?", parent=form_win):
                return
            shutil.rmtree(user_path)
        
        try:
            os.makedirs(user_path)
            with open(os.path.join(user_path, 'details.json'), 'w') as f:
                json.dump(details, f, indent=4)
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save user details: {e}", parent=form_win)
            if os.path.exists(user_path): shutil.rmtree(user_path)
            return

        form_win.destroy()
        self.log_message(f"Saved details for new {user_type}: {name}.")
        self._launch_face_capture_window(name, user_path)

    def _launch_face_capture_window(self, name, user_path):
        reg_window = Toplevel(self.root); reg_window.title(f"Capturing Face: {name}"); reg_window.geometry("820x600")
        reg_window.resizable(False, False); reg_window.configure(bg=self.COLOR_PRIMARY); reg_window.transient(self.root); reg_window.grab_set()
        
        reg_label = Label(reg_window, bg=self.COLOR_SECONDARY); reg_label.pack(padx=10, pady=10)
        info_label = ttk.Label(reg_window, text="Preparing camera...", font=("Segoe UI", 12, "bold")); info_label.pack(pady=5)
        quality_label = ttk.Label(reg_window, text="", font=("Segoe UI", 10, "italic")); quality_label.pack(pady=2)
        progress = ttk.Progressbar(reg_window, orient=HORIZONTAL, length=400, mode='determinate'); progress.pack(pady=10)
        
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - reg_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - reg_window.winfo_height()) // 2
        reg_window.geometry(f"+{x}+{y}")

        self.capture_running_event = threading.Event(); self.capture_running_event.set()
        threading.Thread(target=self._capture_faces_worker, args=(name, user_path, reg_window, reg_label, info_label, quality_label, progress), daemon=True).start()
        reg_window.protocol("WM_DELETE_WINDOW", lambda: self.on_registration_cancel(reg_window, user_path))

    def _capture_faces_worker(self, name, user_path, reg_window, reg_label, info_label, quality_label, progress):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            if reg_window.winfo_exists(): messagebox.showerror("Camera Error", "Cannot open camera.", parent=reg_window)
            self.on_registration_cancel(reg_window, user_path, confirmed=True); return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        count, total_images, BLUR_THRESHOLD = 0, 80, 100.0
        prompts = {0: "Look STRAIGHT", 15: "Look slightly UP", 30: "Look slightly DOWN", 45: "Turn head LEFT", 60: "Turn head RIGHT"}
        
        while self.capture_running_event.is_set() and count < total_images:
            ret, frame = cap.read()
            if not ret or not reg_window.winfo_exists(): break
            
            frame = cv2.flip(frame, 1); gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 6, minSize=(150, 150))
            current_prompt = next(prompts[p] for p in sorted(prompts.keys(), reverse=True) if count >= p)
            display_frame, info_text, quality_text = frame.copy(), "No face detected.", ""
            box_color = self.CV_COLOR_DANGER

            if len(faces) == 1:
                (x, y, w, h) = faces[0]; face_roi_gray = gray[y:y+h, x:x+w]
                laplacian_var = cv2.Laplacian(face_roi_gray, cv2.CV_64F).var(); is_blurry = laplacian_var < BLUR_THRESHOLD
                if w < 200 or h < 200: quality_text, box_color = "Please move closer.", self.CV_COLOR_WARNING
                elif is_blurry: quality_text, box_color = "Blurry image, hold still.", self.CV_COLOR_WARNING
                else:
                    quality_text, box_color = "Excellent! Capturing...", self.CV_COLOR_SUCCESS
                    info_text = f"{current_prompt} ({count+1}/{total_images})"
                    face_img_to_save = frame[y:y+h, x:x+w]
                    cv2.imwrite(os.path.join(user_path, f"{count}.jpg"), face_img_to_save)
                    count += 1; time.sleep(0.05)
                cv2.rectangle(display_frame, (x,y), (x+w, y+h), box_color, 2)
            elif len(faces) > 1: info_text = "ERROR: Multiple faces detected!"
            
            def update_reg_ui(img_tk):
                if reg_window.winfo_exists():
                    info_label.config(text=info_text); quality_label.config(text=quality_text)
                    progress.config(value=count * (100 / total_images)); reg_label.config(image=img_tk); reg_label.imgtk = img_tk
            
            img = cv2.resize(display_frame, (800, 450)); imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
            if self.root.winfo_exists(): self.root.after(0, update_reg_ui, imgtk)
        
        cap.release()
        if reg_window.winfo_exists(): reg_window.destroy()

        if self.capture_running_event.is_set():
            if self.root.winfo_exists():
                self.root.after(0, self._finalize_registration, name)
        else:
            self.log_message("Registration cancelled. Restarting camera.")
            if self.root.winfo_exists():
                self.root.after(100, self.start_camera)

    def _finalize_registration(self, name):
        """
        Runs on the main GUI thread after face capture is complete.
        Handles logging, model reloading, and restarting the camera safely.
        """
        messagebox.showinfo("Success", f"Registration complete for {name}.", parent=self.root)
        self.log_message(f"Registration for {name} successful. Rebuilding face database...")
        self._update_status("Status: Rebuilding face database. Please wait...", self.COLOR_WARNING)
        
        self._clear_deepface_cache()
        
        db_thread = threading.Thread(target=self._initialize_models_and_verify_db, daemon=True)
        db_thread.start()
        
        self.root.after(100, self._wait_for_db_and_restart_camera)

    def _wait_for_db_and_restart_camera(self):
        """Periodically checks if the database thread is done, then restarts the camera."""
        current_status = self.status_label.cget("text")
        if "Loading" in current_status or "Rebuilding" in current_status or "Checking" in current_status:
            self.root.after(200, self._wait_for_db_and_restart_camera)
        else:
            self.log_message("Database processing finished. Restarting camera.")
            self.start_camera()
            
    def _clear_deepface_cache(self):
        """Finds and removes the DeepFace representation pickle file."""
        try:
            pkl_file_name = f"representations_{self.DEEPFACE_MODEL.lower()}.pkl"
            pkl_path = os.path.join(self.db_path, pkl_file_name)
            if os.path.exists(pkl_path):
                os.remove(pkl_path)
                self.log_message(f"Removed stale database cache: {pkl_file_name}")
        except Exception as e:
            self.log_message(f"Warning: Could not remove database cache file. It might be in use. Error: {e}")

    def on_registration_cancel(self, reg_window, user_path, confirmed=False):
        if confirmed or messagebox.askyesno("Cancel Registration?", "All captured images for this user will be deleted.", parent=reg_window):
            self.capture_running_event.clear()
            if os.path.exists(user_path):
                try:
                    shutil.rmtree(user_path)
                    self.log_message("Registration cancelled by user and data deleted.")
                except Exception as e:
                    self.log_message(f"Error deleting user data on cancel: {e}")
            if reg_window.winfo_exists():
                reg_window.destroy()

    def mark_attendance(self, name):
        now = datetime.now()
        if name in self.recently_logged and now < self.recently_logged[name]:
            return

        folder_name = name.replace(' ', '_')
        detail_path = os.path.join(self.db_path, folder_name, 'details.json')

        if not os.path.exists(detail_path):
            self.log_message(f"ERROR: Details file not found for {name}. Cannot mark attendance.")
            return

        try:
            with open(detail_path, 'r') as f: details = json.load(f)
        except Exception as e:
            self.log_message(f"ERROR: Could not read details for {name}: {e}"); return
        
        user_type = details.get('user_type', 'Unknown')
        department = details.get('department', 'N/A')

        if user_type == 'Student':
            target_file = self.student_attendance_file
            columns = ["Name", "Department", "Date", "Time"]
            entry_data = [[name, department, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')]]
        elif user_type == 'Faculty':
            target_file = self.faculty_attendance_file
            columns = ["Name", "Department", "Date", "Time"]
            entry_data = [[name, department, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')]]
        else:
            self.log_message(f"WARNING: Unknown user type '{user_type}' for {name}. Attendance not logged.")
            return

        with self.write_lock:
            try:
                entry = pd.DataFrame(entry_data, columns=columns)
                entry.to_csv(target_file, mode='a', header=not os.path.exists(target_file) or os.path.getsize(target_file) == 0, index=False)
                
                self.log_message(f"LOGGED: {name} ({department}) at {now.strftime('%H:%M:%S')}")
                self.recently_logged[name] = now + timedelta(seconds=self.LOG_COOLDOWN_SECONDS)
                self.locked_in_person = None
                self.recognition_history.clear()
                if self.root.winfo_exists():
                    self.mark_attendance_btn.config(state=DISABLED)
            except Exception as e:
                self.log_message(f"ERROR writing to {target_file}: {e}")

    def log_message(self, msg):
        def _log():
            if self.attendance_box.winfo_exists():
                self.attendance_box.config(state=NORMAL)
                self.attendance_box.insert(END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
                self.attendance_box.see(END)
                self.attendance_box.config(state=DISABLED)
        if hasattr(self, 'root') and self.root.winfo_exists(): self.root.after(0, _log)

    def clear_log(self):
        self.attendance_box.config(state=NORMAL)
        self.attendance_box.delete(1.0, END)
        self.attendance_box.config(state=DISABLED)
        self.log_message("Log cleared.")

    def show_stats(self):
        stats_win = Toplevel(self.root)
        title = "Admin: Manage Users" if self.role == "admin" else "View Registered Students"
        stats_win.title(title)
        stats_win.geometry("1100x600") 
        stats_win.configure(bg=self.COLOR_PRIMARY)
        stats_win.transient(self.root); stats_win.grab_set()
        
        ttk.Label(stats_win, text="Double-click a name to see details", font=("Segoe UI", 12, "italic"), foreground=self.COLOR_TEXT_LIGHT).pack(pady=10)
        tree_frame = ttk.Frame(stats_win); tree_frame.pack(expand=True, fill=BOTH, padx=10, pady=5)
        tree = ttk.Treeview(tree_frame, columns=("name",), show="headings", style="Treeview")
        tree.heading("name", text="Registered User"); tree.pack(side=LEFT, expand=True, fill=BOTH)
        tree.tag_configure('user_item', foreground=self.COLOR_TEXT_LIGHT)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); scrollbar.pack(side=RIGHT, fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        self.populate_users_tree(tree)
        tree.bind("<Double-1>", lambda e: self.show_user_details(tree, stats_win))
        
        button_frame_stats = ttk.Frame(stats_win); button_frame_stats.pack(pady=10, fill=X, padx=10, ipady=5)
        
        if self.role == "admin": 
            ttk.Button(button_frame_stats, text="🎓 View Student Log", command=self.show_student_attendance_log, style="TButton").pack(side=LEFT, expand=True, padx=5)
            ttk.Button(button_frame_stats, text="💼 View Faculty Log", command=self.show_faculty_attendance_log, style="TButton").pack(side=LEFT, expand=True, padx=5)
            ttk.Button(button_frame_stats, text="🗑️ Delete Selected User", command=lambda: self.delete_user(tree), style="Danger.TButton").pack(side=LEFT, expand=True, padx=5)
            ttk.Button(button_frame_stats, text="✉️ Alert Absentees", command=lambda: self.show_absentee_alert_popup(stats_win), style="Warning.TButton").pack(side=LEFT, expand=True, padx=5)
            ttk.Button(button_frame_stats, text="💰 Calculate Faculty Salaries", command=lambda: self.show_salary_calculator(stats_win), style="Success.TButton").pack(side=LEFT, expand=True, padx=5)
        else:
             ttk.Button(button_frame_stats, text="📜 View Attendance Log", command=self.show_student_attendance_log, style="TButton").pack(side=LEFT, expand=True, padx=5)

    def get_absent_users(self):
        all_users = []
        try:
            user_folders = [d for d in os.listdir(self.db_path) if os.path.isdir(os.path.join(self.db_path, d))]
            for folder_name in user_folders:
                display_name = folder_name.replace('_', ' ')
                details_path = os.path.join(self.db_path, folder_name, 'details.json')
                try:
                    if os.path.exists(details_path):
                        with open(details_path, 'r') as f: details = json.load(f)
                        display_name = details.get('name', display_name)
                except (FileNotFoundError, json.JSONDecodeError): pass 
                all_users.append({'name': display_name, 'folder_name': folder_name})
        except FileNotFoundError: return [] 

        present_today = set()
        today_str = datetime.now().strftime('%Y-%m-%d')
        for attendance_file in [self.student_attendance_file, self.faculty_attendance_file]:
            try:
                if os.path.exists(attendance_file):
                    df = pd.read_csv(attendance_file)
                    if not df.empty:
                        today_df = df[df['Date'] == today_str]
                        present_today.update(today_df['Name'].unique())
            except (FileNotFoundError, pd.errors.EmptyDataError): pass 

        return [user for user in all_users if user['name'] not in present_today]

    def show_absentee_alert_popup(self, parent_win):
        absent_users = self.get_absent_users()
        if not absent_users:
            messagebox.showinfo("All Present", "No absent users found for today.", parent=parent_win)
            return

        absentee_win = Toplevel(parent_win)
        absentee_win.title("Absent Users Today"); absentee_win.geometry("650x500") 
        absentee_win.configure(bg=self.COLOR_PRIMARY); absentee_win.transient(parent_win); absentee_win.grab_set()

        ttk.Label(absentee_win, text="Select a person and click 'Send Alert'", font=("Segoe UI", 12)).pack(pady=10)
        tree_frame = ttk.Frame(absentee_win); tree_frame.pack(expand=True, fill=BOTH, padx=10, pady=5)
        tree = ttk.Treeview(tree_frame, columns=("name", "type"), show="headings", style="Treeview")
        tree.heading("name", text="Absent Person"); tree.column("name", width=250)
        tree.heading("type", text="User Type"); tree.column("type", width=100, anchor='center')
        tree.pack(side=LEFT, expand=True, fill=BOTH)
        tree.tag_configure('user_item', foreground=self.COLOR_TEXT_LIGHT)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); scrollbar.pack(side=RIGHT, fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        for user in absent_users:
            folder_name = user['folder_name']; display_name = user['name']
            user_type = "Unknown"
            try:
                with open(os.path.join(self.db_path, folder_name, 'details.json'), 'r') as f:
                    details = json.load(f); user_type = details.get('user_type', 'User').title()
            except Exception: pass
            tree.insert("", "end", values=(display_name, user_type), iid=folder_name, tags=('user_item',))

        def send_alert_from_popup():
            selected_item_id = tree.focus()
            if not selected_item_id:
                messagebox.showwarning("Selection Error", "Please select a person from the list.", parent=absentee_win)
                return
            self.send_alert_to_user(selected_item_id, absentee_win)

        button_frame = ttk.Frame(absentee_win)
        button_frame.pack(pady=10, fill=X, padx=10, ipady=5)
        ttk.Button(button_frame, text="✉️ Send Alert to Selected", command=send_alert_from_popup, style="Success.TButton").pack(side=LEFT, expand=True, padx=5)
        ttk.Button(button_frame, text="Close", command=absentee_win.destroy).pack(side=RIGHT, expand=True, padx=5)

    def send_alert_to_user(self, folder_name, parent_win):
        detail_path = os.path.join(self.db_path, folder_name, 'details.json')
        if not os.path.exists(detail_path):
            messagebox.showerror("Error", f"Details file not found for user.", parent=parent_win); return
        try:
            with open(detail_path, 'r') as f: details = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read details file: {e}", parent=parent_win); return

        name = details.get('name', folder_name.replace('_', ' ')); phone_number = details.get('phone_number')
        user_type = details.get('user_type', 'User')

        if not phone_number:
            messagebox.showerror("No Phone Number", f"No phone number is registered for {name}.", parent=parent_win); return

        now = datetime.now()
        message = (f"ABSENCE ALERT\n\n"
                   f"This is to inform you that the {user_type.lower()} '{name}' "
                   f"was marked absent on {now.strftime('%A, %B %d, %Y')} "
                   f"at {now.strftime('%I:%M %p')}.")
        
        if messagebox.askyesno("Confirm Message", 
                           f"This will attempt to automatically send the following message to {name} ({phone_number}):\n\n"
                           f"'{message}'\n\n"
                           f"Do you want to proceed?",
                           parent=parent_win):
            self.log_message(f"Preparing to send absence alert to {name} via MS Edge.")
            threading.Thread(target=self._send_whatsapp_worker, args=(phone_number, message, parent_win), daemon=True).start()

    def _send_whatsapp_worker(self, phone_number, message, parent_win):
        try:
            send_button_image = 'send_button.png'
            if not os.path.exists(send_button_image):
                error_message = (f"Automation Error: '{send_button_image}' not found.\n\n"
                                 "To enable automatic sending, please take a screenshot of the WhatsApp 'Send' button (the paper plane icon) "
                                 "and save it as 'send_button.png' in the same folder as the script.")
                self.log_message(f"ERROR: {error_message}")
                self.root.after(0, lambda: messagebox.showerror("File Not Found", error_message, parent=parent_win))
                return

            edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
            if not os.path.exists(edge_path):
                edge_path_64 = "C:/Program Files/Microsoft/Edge/Application/msedge.exe"
                if os.path.exists(edge_path_64): edge_path = edge_path_64
                else:
                    error_message = "Microsoft Edge not found. Please check installation path."
                    self.log_message(f"ERROR: {error_message}")
                    self.root.after(0, lambda: messagebox.showerror("Browser Not Found", error_message, parent=parent_win)); return

            webbrowser.register('msedge', None, webbrowser.BackgroundBrowser(edge_path))
            encoded_message = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
            webbrowser.get('msedge').open(url)
            self.log_message(f"Opened WhatsApp for {phone_number}. Waiting for page to load...")
            time.sleep(12)

            send_button_location = None; start_time = time.time(); timeout = 30 
            while time.time() - start_time < timeout:
                try:
                    send_button_location = pyautogui.locateCenterOnScreen(send_button_image, confidence=0.9)
                    if send_button_location:
                        self.log_message("Send button found. Sending message."); break
                except pyautogui.PyAutoGUIException as e:
                    if "needle" in str(e).lower() and "haystack" in str(e).lower():
                         self.log_message("ERROR: DPI scaling issue detected by PyAutoGUI. Aborting automation.")
                         self.root.after(0, lambda: messagebox.showerror("Automation Error", f"A screen scaling error occurred:\n'{e}'\n\nPlease set your Windows display scaling to 100% and restart the application.", parent=parent_win))
                         return
                    pass
                time.sleep(1)

            if send_button_location:
                pyautogui.click(send_button_location)
                time.sleep(2); pyautogui.hotkey('ctrl', 'w')
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Message sent successfully to {phone_number}!", parent=parent_win))
                self.log_message(f"Automated message sent to {phone_number}.")
            else:
                timeout_error = ("Failed to send message automatically.\n\n"
                                 "Possible reasons:\n"
                                 "• You are not logged into WhatsApp Web.\n"
                                 "• The 'send_button.png' image is incorrect or unclear.\n"
                                 "• The WhatsApp Web page did not load in time.\n\n"
                                 "The chat has been left open for you to send manually.")
                self.log_message("ERROR: Timed out waiting for send button.")
                self.root.after(0, lambda: messagebox.showwarning("Automation Timeout", timeout_error, parent=parent_win))
        except Exception as e:
            error_message = f"An unexpected error occurred during WhatsApp automation: {e}"
            self.log_message(f"ERROR: {error_message}")
            self.root.after(0, lambda: messagebox.showerror("WhatsApp Error", error_message, parent=parent_win))

    def populate_users_tree(self, tree):
        for i in tree.get_children(): tree.delete(i)
        try:
            user_folders = sorted([d for d in os.listdir(self.db_path) if os.path.isdir(os.path.join(self.db_path, d))])
            users_to_display = 0
            for folder_name in user_folders:
                display_name = folder_name.replace('_', ' ')
                try:
                    details_path = os.path.join(self.db_path, folder_name, 'details.json')
                    if not os.path.exists(details_path):
                        if self.role == "user": continue
                    with open(details_path, 'r') as f:
                        details = json.load(f)
                        display_name = details.get('name', display_name)
                        if self.role == "user" and details.get('user_type') != 'Student': continue
                except (FileNotFoundError, json.JSONDecodeError):
                    if self.role == "user": continue
                    pass
                tree.insert("", "end", values=(display_name,), iid=folder_name, tags=('user_item',))
                users_to_display += 1
            if users_to_display == 0:
                msg = "No students registered yet." if self.role == "user" else "No users registered yet."
                tree.insert("", "end", values=(msg,), iid="no_users", tags=('user_item',))
        except FileNotFoundError: tree.insert("", "end", values=("Database directory not found!",), iid="no_db", tags=('user_item',))

    def delete_user(self, tree):
        selected_item = tree.focus()
        if not selected_item or selected_item in ["no_users", "no_db"]:
            messagebox.showwarning("Selection Error", "Please select a user to delete.", parent=tree.winfo_toplevel()); return
        display_name = tree.item(selected_item)['values'][0]; folder_name = selected_item
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete '{display_name}'?\nThis action cannot be undone.", parent=tree.winfo_toplevel()):
            user_path = os.path.join(self.db_path, folder_name)
            try:
                shutil.rmtree(user_path)
                self._clear_deepface_cache()
                messagebox.showinfo("Success", f"User '{display_name}' has been deleted. The face database will now be re-checked.", parent=tree.winfo_toplevel())
                self.log_message(f"Deleted user: {display_name}")
                self.populate_users_tree(tree)
                threading.Thread(target=self._initialize_models_and_verify_db, daemon=True).start()
            except Exception as e: messagebox.showerror("Deletion Failed", f"An error occurred while deleting the user: {e}", parent=tree.winfo_toplevel())

    def _display_attendance_log(self, title, filename):
        log_win = Toplevel(self.root)
        log_win.title(title); log_win.geometry("800x600")
        log_win.configure(bg=self.COLOR_PRIMARY); log_win.transient(self.root); log_win.grab_set()

        try:
            df = pd.read_csv(filename)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            ttk.Label(log_win, text="Attendance file is empty or not found.", font=("Segoe UI", 14)).pack(pady=50); return

        cols = list(df.columns)
        tree = ttk.Treeview(log_win, columns=cols, show="headings", style="Treeview")
        for col in cols: tree.heading(col, text=col); tree.column(col, width=150, anchor='center')
        tree.tag_configure('log_item', foreground=self.COLOR_TEXT_LIGHT)
        
        df_sorted = df.sort_values(by=["Date", "Time"], ascending=[False, False])
        for index, row in df_sorted.iterrows():
            tree.insert("", "end", values=list(row), tags=('log_item',))

        vsb = ttk.Scrollbar(log_win, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(log_win, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y'); hsb.pack(side='bottom', fill='x'); tree.pack(expand=True, fill='both', padx=10, pady=10)

    def show_student_attendance_log(self):
        self._display_attendance_log("Student Attendance Log", self.student_attendance_file)
    
    def show_faculty_attendance_log(self):
        self._display_attendance_log("Faculty Attendance Log", self.faculty_attendance_file)

    def show_user_details(self, tree, parent_win):
        selected_item_id = tree.focus()
        if not selected_item_id or selected_item_id in ["no_users", "no_db"]: return
        folder_name = selected_item_id
        detail_path = os.path.join(self.db_path, folder_name, 'details.json')
        if not os.path.exists(detail_path):
            messagebox.showinfo("Details Not Found", f"No details file found for user '{folder_name}'.", parent=parent_win); return
        try:
            with open(detail_path, 'r') as f: details = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Error", f"Could not read details file: {e}", parent=parent_win); return
            
        display_name = details.get('name', folder_name.replace('_', ' '))
        detail_win = Toplevel(parent_win)
        detail_win.title(f"Details for {display_name}"); detail_win.geometry("900x700") 
        detail_win.configure(bg=self.COLOR_PRIMARY); detail_win.transient(parent_win); detail_win.grab_set(); detail_win.resizable(False, False)

        main_frame = ttk.Frame(detail_win, padding=20); main_frame.pack(expand=True, fill=BOTH)
        row = 0
        for key, value in details.items():
            key_text = key.replace('_', ' ').title()
            if value:
                ttk.Label(main_frame, text=f"{key_text}:", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, sticky="e", padx=10, pady=5)
                ttk.Label(main_frame, text=value, font=("Segoe UI", 11), wraplength=400, anchor="w").grid(row=row, column=1, sticky="w", padx=10, pady=5)
                row += 1
                
        ttk.Separator(main_frame, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky='ew', pady=10); row += 1
        ttk.Label(main_frame, text="Registered Face Samples:", font=("Segoe UI", 11, "bold")).grid(row=row, column=0, columnspan=2, sticky='w', padx=10); row += 1
        
        img_frame = ttk.Frame(main_frame); img_frame.grid(row=row, columnspan=2, pady=10); detail_win.images = []
        try:
            user_image_path = os.path.join(self.db_path, folder_name)
            image_files = sorted([f for f in os.listdir(user_image_path) if f.endswith('.jpg')], key=lambda x: int(os.path.splitext(x)[0]))
            if not image_files: ttk.Label(img_frame, text="No images found.").pack()
            
            for i, img_file in enumerate(image_files[:8]):
                img_path = os.path.join(user_image_path, img_file); img = Image.open(img_path)
                img.thumbnail((100, 100)); photo = ImageTk.PhotoImage(img)
                detail_win.images.append(photo)
                img_label = ttk.Label(img_frame, image=photo, relief="solid"); img_label.grid(row=0, column=i, padx=5, pady=5)
        except Exception as e: 
            ttk.Label(img_frame, text=f"Error loading images: {e}").pack()
            
        row += 1
        ttk.Button(main_frame, text="Close", command=detail_win.destroy).grid(row=row, columnspan=2, pady=20)

    def show_salary_calculator(self, parent_win):
        calc_win = Toplevel(parent_win)
        calc_win.title("Faculty Salary Calculator"); calc_win.geometry("1200x700") 
        calc_win.configure(bg=self.COLOR_PRIMARY); calc_win.transient(parent_win); calc_win.grab_set()
        self.salary_data_for_export = []

        input_frame = ttk.Frame(calc_win, padding=10); input_frame.pack(fill=X, pady=5)
        ttk.Label(input_frame, text="From (YYYY-MM-DD):").pack(side=LEFT, padx=(10, 5))
        start_date_entry = ttk.Entry(input_frame, width=15); start_date_entry.pack(side=LEFT, padx=5)
        start_date_entry.insert(0, (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))

        ttk.Label(input_frame, text="To (YYYY-MM-DD):").pack(side=LEFT, padx=(20, 5))
        end_date_entry = ttk.Entry(input_frame, width=15); end_date_entry.pack(side=LEFT, padx=5)
        end_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        
        tree_frame = ttk.Frame(calc_win, padding=10); tree_frame.pack(expand=True, fill=BOTH)
        cols = ("Name", "Department", "Basis", "Rate", "Present", "Absent", "Deduction", "Final Salary", "Remarks")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col); tree.column(col, width=110, anchor='center')
        tree.column("Name", width=160, anchor='w'); tree.column("Remarks", width=300, anchor='w')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview); hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y'); hsb.pack(side='bottom', fill='x'); tree.pack(expand=True, fill='both')

        export_button = ttk.Button(input_frame, text="Export to CSV", style="TButton", state=DISABLED, command=lambda: self._export_salaries_to_csv(calc_win))
        export_button.pack(side=LEFT, padx=20)
        
        calc_button = ttk.Button(input_frame, text="Calculate Salaries", style="Success.TButton",
            command=lambda: self._calculate_and_populate_salaries(start_date_entry.get(), end_date_entry.get(), tree, calc_win, export_button))
        calc_button.pack(side=LEFT, padx=5)

    def _calculate_and_populate_salaries(self, start_date_str, end_date_str, tree, parent_win, export_button):
        for i in tree.get_children(): tree.delete(i)
        self.salary_data_for_export = []; export_button.config(state=DISABLED)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if start_date > end_date:
                messagebox.showerror("Date Error", "Start date cannot be after end date.", parent=parent_win); return
        except ValueError:
            messagebox.showerror("Date Error", "Invalid date format. Please use YYYY-MM-DD.", parent=parent_win); return

        try:
            attendance_df = pd.read_csv(self.faculty_attendance_file)
            attendance_df['Date'] = pd.to_datetime(attendance_df['Date']).dt.date
        except (FileNotFoundError, pd.errors.EmptyDataError):
            messagebox.showinfo("No Data", "Faculty attendance file is empty or not found.", parent=parent_win); return

        faculty_folders = []
        user_folders = [d for d in os.listdir(self.db_path) if os.path.isdir(os.path.join(self.db_path, d))]
        for folder in user_folders:
            detail_path = os.path.join(self.db_path, folder, 'details.json')
            if os.path.exists(detail_path):
                try:
                    with open(detail_path, 'r') as f:
                        details = json.load(f)
                        if details.get('user_type') == 'Faculty': faculty_folders.append((folder, details))
                except (json.JSONDecodeError, IOError): continue
        
        if not faculty_folders:
            messagebox.showinfo("No Faculty", "No faculty members found in the database.", parent=parent_win); return

        num_days_in_period = (end_date - start_date).days + 1
        calculated_data = []

        for folder, details in faculty_folders:
            name = details.get('name', folder.replace('_', ' ')); dept = details.get('department', 'N/A')
            salary_type = details.get('salary_type')
            
            mask = (attendance_df['Name'] == name) & (attendance_df['Date'] >= start_date) & (attendance_df['Date'] <= end_date)
            user_attendance = attendance_df.loc[mask]
            present_days = len(user_attendance['Date'].unique())
            absent_days = num_days_in_period - present_days
            
            basis, rate_str, deduction, final_salary, remarks = "N/A", "0.00", 0.0, 0.0, "Data missing"
            monthly_salary_val, daily_rate_val = 0.0, 0.0
            
            try:
                if salary_type == 'Regular':
                    monthly_salary_val = float(details.get('monthly_salary', 0)); basis = "Monthly"; rate_str = f"{monthly_salary_val:.2f}"
                    daily_rate_val = monthly_salary_val / 30 
                    deduction = daily_rate_val * absent_days if absent_days > 2 else 0 # Example policy
                    remarks = f"Deducted for {absent_days} absences." if deduction > 0 else f"{absent_days} absences (within limit)."
                    final_salary = monthly_salary_val - deduction
                elif salary_type == 'Visiting':
                    visiting_type = details.get('visiting_type'); visiting_rate_val = float(details.get('visiting_rate', 0))
                    rate_str = f"{visiting_rate_val:.2f}"
                    if visiting_type == 'Fixed':
                        basis = "Visiting (Fixed)"
                        final_salary = visiting_rate_val if num_days_in_period >= 30 else 0
                        remarks = "Full fixed amount." if final_salary > 0 else f"Period is {num_days_in_period} days (<30)."
                    elif visiting_type == 'PerDay':
                        basis = "Visiting (Per Day)"; daily_rate_val = visiting_rate_val
                        final_salary = visiting_rate_val * present_days
                        remarks = f"{present_days} present days @ {rate_str}/day."
            except (ValueError, TypeError): remarks = "Invalid salary data in details file."

            tree.insert("", "end", values=(name, dept, basis, rate_str, present_days, absent_days, f"{deduction:.2f}", f"{final_salary:.2f}", remarks))
            calculated_data.append({"name": name, "department": dept, "monthly_salary": monthly_salary_val, "daily_salary": daily_rate_val,
                                    "total_absents": absent_days, "salary_deducted": deduction, "total_salary": final_salary})
        
        self.salary_data_for_export = calculated_data
        if self.salary_data_for_export: export_button.config(state=NORMAL)

    def _export_salaries_to_csv(self, parent_win):
        if not self.salary_data_for_export:
            messagebox.showerror("Export Error", "No salary data to export.", parent=parent_win); return
        try:
            df = pd.DataFrame(self.salary_data_for_export)
            required_cols = ["name", "department", "monthly_salary", "daily_salary", "total_absents", "salary_deducted", "total_salary"]
            for col in required_cols:
                if col not in df.columns: df[col] = 0.0
            df[required_cols].to_csv(self.salary_file, index=False, float_format='%.2f')
            messagebox.showinfo("Export Successful", f"Salary data has been saved to '{self.salary_file}'.", parent=parent_win)
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while saving the CSV file:\n{e}", parent=parent_win)

def login():
    login_win = Toplevel(); login_win.title("User Login"); login_win.attributes('-fullscreen', True)
    BG_COLOR, FORM_BG_COLOR, TEXT_COLOR = "#2C3E50", "#34495E", "#ECF0F1"
    
    style = ttk.Style(login_win); style.theme_use('clam')
    style.configure("TEntry", fieldbackground="#404040", foreground=TEXT_COLOR, insertcolor=TEXT_COLOR, font=("Segoe UI", 11))
    style.configure("Placeholder.TEntry", foreground="#8A8A8A")

    canvas = Canvas(login_win, bg=BG_COLOR, highlightthickness=0); canvas.pack(fill=BOTH, expand=True)
    try:
        if os.path.exists("background.jpg"):
            img = Image.open("background.jpg").resize((login_win.winfo_screenwidth(), login_win.winfo_screenheight()), Image.LANCZOS).filter(ImageFilter.GaussianBlur(15))
            login_win.bg_photo = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=login_win.bg_photo, anchor="nw")
    except Exception: pass

    form_frame = Frame(login_win, bg=FORM_BG_COLOR, width=400, height=350)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")
    form_frame.pack_propagate(False)

    Label(form_frame, text="Face Attendance System", font=("Segoe UI", 16, "bold"), bg=FORM_BG_COLOR, fg=TEXT_COLOR).pack(pady=(40, 30))
    username_entry = PlaceholderEntry(form_frame, "Username", width=40); username_entry.pack(pady=10, padx=40, ipady=8)
    password_entry = PlaceholderEntry(form_frame, "Password", width=40, show='*'); password_entry.pack(pady=10, padx=40, ipady=8)
    login_button = Button(form_frame, text="LOGIN", font=("Segoe UI", 12, "bold"), bg="#E74C3C", fg=TEXT_COLOR, relief="flat", activebackground="#C0392B", activeforeground=TEXT_COLOR, bd=0)
    login_button.pack(pady=(40, 30), ipady=10, ipadx=138)

    def check_credentials(event=None):
        user = username_entry.get()
        if user == username_entry.placeholder: user = ""
        pwd = password_entry.get()
        if pwd == password_entry.placeholder: pwd = ""
        
        role_to_launch = None
        if user == "admin" and pwd == "admin123": role_to_launch = "admin"
        elif user == "user" and pwd == "user123": role_to_launch = "user"
        
        if role_to_launch:
            main_root = login_win.master
            login_win.destroy()
            main_root.deiconify()
            app = FaceRecognitionApp(main_root, role=role_to_launch)
            main_root.protocol("WM_DELETE_WINDOW", app.on_closing)
            main_root.after(100, app.run_initial_setup)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password", parent=login_win)

    login_button.config(command=check_credentials)
    login_win.bind('<Return>', check_credentials)
    login_win.bind('<Escape>', lambda e: login_win.master.destroy())

if __name__ == "__main__":
    root = Tk()
    root.withdraw() 
    login()
    root.mainloop()
