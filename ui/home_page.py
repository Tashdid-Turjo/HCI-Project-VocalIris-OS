import threading
import time
import cv2
import customtkinter as ctk

# Safe dynamic tracking script imports
try:
    from engines.Iris_Voice import run_eyeball_tracking, run_voice_recognition
    from engines.face_detection_test import run_face_detection
except ImportError:
    run_eyeball_tracking = None
    run_voice_recognition = None
    run_face_detection = None

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent, fg_color="transparent")
        
        # Bind access to main app persistent variables
        self.app_master = app_instance
        
        # Configure layout weights
        self.grid_columnconfigure(0, weight=1, uniform="equal")
        self.grid_columnconfigure(1, weight=1, uniform="equal")
        self.grid_rowconfigure(1, weight=1)

        # ==========================================
        # TOP BLOCK: CALIBRATION WIZARD BANNER
        # ==========================================
        self.calibration_card = ctk.CTkFrame(self)
        self.calibration_card.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.calib_title = ctk.CTkLabel(
            self.calibration_card, text="System Alignment Required", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.calib_title.pack(side="left", padx=20, pady=15)
        
        self.calib_btn = ctk.CTkButton(
            self.calibration_card, text="Launch Calibration Wizard", fg_color="#2b82c9", hover_color="#1e5d91"
        )
        self.calib_btn.pack(side="right", padx=20, pady=15)

        # ==========================================
        # LEFT COLUMN CARD: VOICE CONTROL INTERFACE
        # ==========================================
        self.voice_card = ctk.CTkFrame(self)
        self.voice_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.voice_title = ctk.CTkLabel(
            self.voice_card, text="🗣️ Voice Control Engine", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.voice_title.pack(anchor="w", padx=15, pady=15)
        
        self.voice_switch = ctk.CTkSwitch(
            self.voice_card, text="Start Voice Service Listener", command=self.toggle_voice_service
        )
        self.voice_switch.pack(anchor="w", padx=20, pady=5)
        
        # PERSIST STATE: Keep switch visually selected if it was active
        if self.app_master.voice_running:
            self.voice_switch.select()

        # Command Registry Text Box
        self.cmd_box = ctk.CTkTextbox(self.voice_card, activate_scrollbars=True)
        self.cmd_box.pack(fill="both", expand=True, padx=15, pady=15)
        
        cheat_sheet = (
            "--- COMMAND CHEAT-SHEET DICTIONARY ---\n\n"
            "▶ NAVIGATION & SYSTEM ACTIONS:\n"
            " • 'Scroll down' -> Scroll webpage view downwards\n"
            " • 'Move pointer' -> Adjust mouse axis position\n"
            " • 'Left click' -> Left-click highlighted item\n"
            " • 'Right click' -> Open contextual property tray\n"
            " • 'Double click' -> Execute launch selection\n\n"
            "▶ TEXT FIELD & KEYBOARD PIPELINES:\n"
            " • 'Open keyboard' -> Launch visual soft-board overlay\n"
            " • 'Type [Letter]' -> Output specific character key\n"
            " • 'Delete word' -> Wipe out backspace segment\n"
            " • 'Copy text' -> Save highlight buffer to system clipboard\n"
            " • 'Paste text' -> Dump system clipboard string downstream"
        )
        self.cmd_box.insert("0.0", cheat_sheet)
        self.cmd_box.configure(state="disabled")

        # ==========================================
        # RIGHT COLUMN CARD: EYE TRACKING INTERFACE
        # ==========================================
        self.eye_card = ctk.CTkFrame(self)
        self.eye_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.eye_title = ctk.CTkLabel(
            self.eye_card, text="👁️ Eye Tracking Engine", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.eye_title.pack(anchor="w", padx=15, pady=15)
        
        self.eye_switch = ctk.CTkSwitch(
            self.eye_card, text="Start Eye Tracking Engine", command=self.toggle_eye_service
        )
        self.eye_switch.pack(anchor="w", padx=20, pady=5)
        
        # PERSIST STATE: Keep switch visually selected if it was active
        if self.app_master.eye_running:
            self.eye_switch.select()

        # Target Dropdown Setup
        self.mode_label = ctk.CTkLabel(self.eye_card, text="Active Extraction Processing Target:")
        self.mode_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # --- TASK 1: ADDING THE DROPDOWN LISTENER (command=self.on_dropdown_change) ---
        self.mode_dropdown = ctk.CTkOptionMenu(
            self.eye_card, 
            values=["Eyeball Tracking (High Precision)", "Face Tracking (Backup Profile)"],
            command=self.on_dropdown_change  
        )
        self.mode_dropdown.pack(anchor="w", padx=20, pady=0)
        
        # Visual Frame Container for Camera Render Canvas
        self.video_placeholder = ctk.CTkFrame(self.eye_card, fg_color="#1a1a1a", height=200)
        self.video_placeholder.pack(fill="x", padx=15, pady=(35, 15), side="bottom")
        
        self.video_label = ctk.CTkLabel(
            self.video_placeholder, 
            text="[ Hardware Webcam Feed Offline ]", 
            text_color="#555555", font=ctk.CTkFont(size=11, slant="italic")
        )
        self.video_label.pack(expand=True, pady=40)

    # ========================================================
    # INTERFACE THREAD MANAGEMENT LOGIC
    # ========================================================
    def toggle_voice_service(self):
        if self.voice_switch.get() == 1:
            self.app_master.voice_running = True
            print("UI Trigger -> Booting Vosk Microphone Speech Recognition...")
            
            if run_voice_recognition is not None:
                self.voice_thread = threading.Thread(
                    target=run_voice_recognition, 
                    args=(self.app_master,), 
                    daemon=True
                )
            else:
                self.voice_thread = threading.Thread(target=self._bg_voice_loop, daemon=True)
                
            self.voice_thread.start()
        else:
            print("UI Trigger -> Closing microphone listener channels...")
            self.app_master.voice_running = False

    def toggle_eye_service(self):
        selected_mode = self.mode_dropdown.get()
        self.app_master.active_processing_target = selected_mode

        if self.eye_switch.get() == 1:
            self.app_master.eye_running = True
            print(f"UI Trigger -> Initializing Background Line for target: {selected_mode}")
            
            self.eye_thread = threading.Thread(target=self._camera_hardware_pipeline, daemon=True)
            self.eye_thread.start()
        else:
            print("UI Trigger -> Closing tracking line context pipelines...")
            self.app_master.eye_running = False
            self.video_label.configure(image="", text="[ Hardware Webcam Feed Offline ]")
            self.video_label.pack(expand=True, pady=40)

    # --- TASK 2: PUT THE BRAND NEW DROPDOWN AUTOMATION FUNCTION HERE ---
    def on_dropdown_change(self, selected_mode):
        """Triggers immediately when the user changes the dropdown selection."""
        print(f"UI Event -> User switched dropdown to: {selected_mode}")
        
        # Always update the active target state
        self.app_master.active_processing_target = selected_mode
        
        # Hot-reload: If tracking is running, reboot the engine cleanly in the background
        if self.eye_switch.get() == 1 and self.app_master.eye_running:
            print(">>> [Hot-Reload] Changing processing profiles on the fly. Rebooting camera thread...")
            
            # Stop the current engine loop safely
            self.app_master.eye_running = False
            
            # Give the previous hardware pipeline loop a split second to release the camera handle
            time.sleep(0.3)
            
            # Fire up the brand new target script thread immediately!
            self.app_master.eye_running = True
            self.eye_thread = threading.Thread(target=self._camera_hardware_pipeline, daemon=True)
            self.eye_thread.start()

    # ========================================================
    # BACKGROUND LIVE CAMERA PROCESSING PIPELINE
    # ========================================================
    def _camera_hardware_pipeline(self):
        """Dedicated worker thread that queries chosen sub-scripts or falls back cleanly."""
        current_choice = self.app_master.active_processing_target
        print(f">>> [Eye Thread] Booting engine stream route: {current_choice}")

        if "Eyeball" in current_choice and run_eyeball_tracking is not None:
            run_eyeball_tracking(app_callback=self._process_and_draw_frame)
            
        elif "Face" in current_choice and run_face_detection is not None:
            run_face_detection(app_callback=self._process_and_draw_frame)
            
        else:
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            while self.app_master.eye_running:
                ret, frame = cap.read()
                if not ret:
                    break
                if not self._process_and_draw_frame(frame):
                    break
            cap.release()

    def _process_and_draw_frame(self, frame):
        """Accepts an OpenCV frame matrix, formats it for Tkinter, and prints it onto the UI."""
        from PIL import Image, ImageTk
        import cv2

        if not self.app_master.eye_running:
            return False

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            resized_img = pil_img.resize((420, 200), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(image=resized_img)
            
            self.video_label.configure(image=tk_img, text="")
            self.video_label.image = tk_img  
            self.video_label.pack(fill="both", expand=True, padx=0, pady=0)
            return True
        except Exception as e:
            print(f"Frame translation rendering failure anomaly: {e}")
            return False

    # Fallback simulation functions if imports fail
    def _bg_voice_loop(self):
        print(">>> [Voice Thread] Connected to Microphone Stream. Listening...")
        while self.app_master.voice_running:
            time.sleep(2)