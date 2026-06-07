import threading
import time
import customtkinter as ctk

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
        
        # PERSIST STATE: Check if voice was running globally and toggle visual look accordingly
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
        
        # PERSIST STATE: Check if eye tracking was running globally and toggle visual look accordingly
        if self.app_master.eye_running:
            self.eye_switch.select()

        # Dropdown
        self.mode_label = ctk.CTkLabel(self.eye_card, text="Active Extraction Processing Target:")
        self.mode_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.mode_dropdown = ctk.CTkOptionMenu(
            self.eye_card, values=["Eyeball Tracking (High Precision)", "Face Tracking (Backup Profile)"]
        )
        self.mode_dropdown.pack(anchor="w", padx=20, pady=0)
        
        # Visual Placeholder
        self.video_placeholder = ctk.CTkFrame(self.eye_card, fg_color="#1a1a1a", height=200)
        self.video_placeholder.pack(fill="x", padx=15, pady=(35, 15), side="bottom")
        
        self.video_label = ctk.CTkLabel(
            self.video_placeholder, 
            text="[ Local Hardware Webcam Feed Overlay Canvas ]\n(Will bind via background OpenCV frames later)", 
            text_color="#555555", font=ctk.CTkFont(size=11, slant="italic")
        )
        self.video_label.pack(expand=True, pady=40)

    # ========================================================
    # THREAD CONTROLLER CONTROLS
    # ========================================================
    def toggle_voice_service(self):
        if self.voice_switch.get() == 1:
            self.app_master.voice_running = True
            print("UI Trigger -> Starting Voice Service Worker Thread...")
            self.voice_thread = threading.Thread(target=self._bg_voice_loop, daemon=True)
            self.voice_thread.start()
        else:
            print("UI Trigger -> Stopping Voice Service. Raising stop flag...")
            self.app_master.voice_running = False

    def toggle_eye_service(self):
        if self.eye_switch.get() == 1:
            self.app_master.eye_running = True
            print("UI Trigger -> Starting Eye Tracking Camera Worker Thread...")
            self.eye_thread = threading.Thread(target=self._bg_eye_loop, daemon=True)
            self.eye_thread.start()
        else:
            print("UI Trigger -> Stopping Eye Tracking Camera. Raising stop flag...")
            self.app_master.eye_running = False

    # ========================================================
    # HARDWARE SERVICE RE-ENTRANT WORKERS
    # ========================================================
    def _bg_voice_loop(self):
        print(">>> [Voice Thread] Connected to Microphone Stream. Listening...")
        while self.app_master.voice_running:
            print(">>> [Voice Thread] Listening for commands...")
            time.sleep(2)
        print(">>> [Voice Thread] Stopped safely. Microphone pipeline released.")

    def _bg_eye_loop(self):
        print(">>> [Eye Thread] Connected to Webcam Hardware Link. Processing frames...")
        while self.app_master.eye_running:
            print(">>> [Eye Thread] Extracting facial landmark array matrix data...")
            time.sleep(1.5)
        print(">>> [Eye Thread] Stopped safely. Webcam pipeline hardware link released.")