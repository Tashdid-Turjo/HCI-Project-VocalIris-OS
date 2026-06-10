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
        self.current_lang = self.app_master.settings.get("language", "English")
        
        # Configure layout weights
        self.grid_columnconfigure(0, weight=1, uniform="equal")
        self.grid_columnconfigure(1, weight=1, uniform="equal")
        self.grid_rowconfigure(1, weight=1)

        # =================================================================
        # MULTI-LINE COMMAND CHEAT-SHEET DICTIONARY LOCALIZATION
        # =================================================================
        cheat_sheet_en = (
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

        cheat_sheet_bn = (
            "--- ভয়েস কমান্ড চিট-শিট ডিকশনারি ---\n\n"
            "▶ নেভিগেশন এবং সিস্টেম অ্যাকশনসমূহ:\n"
            " • 'Scroll down' -> ওয়েবপেজ স্ক্রোল করে নিচের দিকে নামুন\n"
            " • 'Move pointer' -> মাউসের কার্সার পজিশন সমন্বয় করুন\n"
            " • 'Left click' -> সিলেক্টেড আইটেমে লেফট-ক্লিক করুন\n"
            " • 'Right click' -> কনটেক্সট মেনু বা প্রোপার্টি ট্রে ওপেন করুন\n"
            " • 'Double click' -> ডাবল-ক্লিক করে সিলেকশন রান করুন\n\n"
            "▶ টেক্সট ফিল্ড এবং কীবোর্ড পাইপলাইনসমূহ:\n"
            " • 'Open keyboard' -> ভার্চুয়াল সফট-কীবোর্ড ওভারলে চালু করুন\n"
            " • 'Type [Letter]' -> নির্দিষ্ট ক্যারেক্টার বা অক্ষর টাইপ করুন\n"
            " • 'Delete word' -> ব্যাকস্পেস দিয়ে পূর্ববর্তী শব্দ মুছে ফেলুন\n"
            " • 'Copy text' -> হাইলাইটেড টেক্সট ক্লিপবোর্ডে সেভ করুন\n"
            " • 'Paste text' -> ক্লিপবোর্ডের টেক্সট নির্দিষ্ট স্থানে পেস্ট করুন"
        )

        # ==========================================
        # ELEMENT-BY-ELEMENT TRANSLATION DICTIONARY
        # ==========================================
        self.translations = {
            "English": {
                "calib_title": "System Alignment Required",
                "calib_btn": "Launch Calibration Wizard",
                "voice_title": "🗣️ Voice Control Engine",
                "voice_switch": "Start Voice Service Listener",
                "eye_title": "👁️ Eye Tracking Engine",
                "eye_switch": "Start Eye Tracking Engine",
                "dropdown_lbl": "Active Extraction Processing Target:",
                "dropdown_opts": ["Eyeball Tracking (High Precision)", "Face Tracking (Backup Profile)"],
                "cam_offline": "[ Hardware Webcam Feed Offline ]",
                "cam_switching": "[ Switching Engine Profiles... ]",
                "cheat_sheet": cheat_sheet_en
            },
            "Bangla": {
                "calib_title": "সিস্টেম অ্যালাইনমেন্ট প্রয়োজন",
                "calib_btn": "ক্যালিব্রেশন উইজার্ড চালু করুন",
                "voice_title": "🗣️ ভয়েস কন্ট্রোল ইঞ্জিন",
                "voice_switch": "ভয়েস সার্ভিস লিসেনার চালু করুন",
                "eye_title": "👁️ আই ট্র্যাকিং ইঞ্জিন",
                "eye_switch": "আই ট্র্যাকিং ইঞ্জিন চালু করুন",
                "dropdown_lbl": "সক্রিয় এক্সট্রাকশন প্রসেসিং টার্গেট:",
                "dropdown_opts": ["আইবল ট্র্যাকিং (উচ্চ নির্ভুলতা)", "ফেস ট্র্যাকিং (ব্যাকআপ প্রোফাইল)"],
                "cam_offline": "[ হার্ডওয়্যার ওয়েবক্যাম ফিড অফলাইন ]",
                "cam_switching": "[ ইঞ্জিন প্রোফাইল পরিবর্তন হচ্ছে... ]",
                "cheat_sheet": cheat_sheet_bn
            }
        }

        # Select the active text translation bundle
        self.text_bundle = self.translations.get(self.current_lang, self.translations["English"])

        # ==========================================
        # TOP BLOCK: CALIBRATION WIZARD BANNER
        # ==========================================
        self.calibration_card = ctk.CTkFrame(self)
        self.calibration_card.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.calib_title = ctk.CTkLabel(
            self.calibration_card, text=self.text_bundle["calib_title"], font=ctk.CTkFont(size=16, weight="bold")
        )
        self.calib_title.pack(side="left", padx=20, pady=15)
        
        self.calib_btn = ctk.CTkButton(
            self.calibration_card, text=self.text_bundle["calib_btn"], fg_color="#2b82c9", hover_color="#1e5d91"
        )
        self.calib_btn.pack(side="right", padx=20, pady=15)

        # ==========================================
        # LEFT COLUMN CARD: VOICE CONTROL INTERFACE
        # ==========================================
        self.voice_card = ctk.CTkFrame(self)
        self.voice_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.voice_title = ctk.CTkLabel(
            self.voice_card, text=self.text_bundle["voice_title"], font=ctk.CTkFont(size=16, weight="bold")
        )
        self.voice_title.pack(anchor="w", padx=15, pady=15)
        
        self.voice_switch = ctk.CTkSwitch(
            self.voice_card, text=self.text_bundle["voice_switch"], command=self.toggle_voice_service
        )
        self.voice_switch.pack(anchor="w", padx=20, pady=5)
        
        if self.app_master.voice_running:
            self.voice_switch.select()

        # Command Registry Text Box
        self.cmd_box = ctk.CTkTextbox(self.voice_card, activate_scrollbars=True)
        self.cmd_box.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.cmd_box.insert("0.0", self.text_bundle["cheat_sheet"])
        self.cmd_box.configure(state="disabled")

        # ==========================================
        # RIGHT COLUMN CARD: EYE TRACKING INTERFACE
        # ==========================================
        self.eye_card = ctk.CTkFrame(self)
        self.eye_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.eye_title = ctk.CTkLabel(
            self.eye_card, text=self.text_bundle["eye_title"], font=ctk.CTkFont(size=16, weight="bold")
        )
        self.eye_title.pack(anchor="w", padx=15, pady=15)
        
        self.eye_switch = ctk.CTkSwitch(
            self.eye_card, text=self.text_bundle["eye_switch"], command=self.toggle_eye_service
        )
        self.eye_switch.pack(anchor="w", padx=20, pady=5)
        
        if self.app_master.eye_running:
            self.eye_switch.select()

        # Target Dropdown Setup
        self.mode_label = ctk.CTkLabel(self.eye_card, text=self.text_bundle["dropdown_lbl"])
        self.mode_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.mode_dropdown = ctk.CTkOptionMenu(
            self.eye_card, 
            values=self.text_bundle["dropdown_opts"],
            command=self.on_dropdown_change  
        )
        self.mode_dropdown.pack(anchor="w", padx=20, pady=0)
        
        # Safe default population from master tracker config memory states
        saved_target = getattr(self.app_master, 'active_processing_target', None)
        if saved_target:
            # Keep language configuration strings accurate if changed on hot reload
            if "Eyeball" in saved_target or "আইবল" in saved_target:
                self.mode_dropdown.set(self.text_bundle["dropdown_opts"][0])
            else:
                self.mode_dropdown.set(self.text_bundle["dropdown_opts"][1])

        # Visual Frame Container for Camera Render Canvas
        self.video_placeholder = ctk.CTkFrame(self.eye_card, fg_color="#1a1a1a", height=200)
        self.video_placeholder.pack(fill="x", padx=15, pady=(35, 15), side="bottom")
        
        initial_cam_text = self.text_bundle["cam_switching"] if self.app_master.eye_running else self.text_bundle["cam_offline"]
        self.video_label = ctk.CTkLabel(
            self.video_placeholder, 
            text=initial_cam_text, 
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
            
            self.video_label.configure(image="", text=self.text_bundle["cam_offline"])
            self.video_label.image = None  
            self.video_label.pack(fill="none", expand=True, pady=40)

    def on_dropdown_change(self, selected_mode):
        print(f"UI Event -> User switched dropdown to: {selected_mode}")
        self.app_master.active_processing_target = selected_mode
        
        if self.eye_switch.get() == 1 and self.app_master.eye_running:
            print(">>> [Hot-Reload] Changing processing profiles. Stopping old thread first...")
            self.app_master.eye_running = False
            
            self.video_label.configure(image="", text=self.text_bundle["cam_switching"])
            self.video_label.image = None
            
            self.after(400, self._restart_eye_thread)
        else:
            self.video_label.configure(image="", text=self.text_bundle["cam_offline"])
            self.video_label.image = None
            self.video_label.pack(fill="none", expand=True, pady=40)

    # ========================================================
    # BACKGROUND LIVE CAMERA PROCESSING PIPELINE
    # ========================================================
    def _camera_hardware_pipeline(self):
        current_choice = self.app_master.active_processing_target
        print(f">>> [Eye Thread] Booting engine stream route: {current_choice}")

        if ("Eyeball" in current_choice or "আইবল" in current_choice) and run_eyeball_tracking is not None:
            run_eyeball_tracking(app_callback=self._process_and_draw_frame)
            
        elif ("Face" in current_choice or "ফেস" in current_choice) and run_face_detection is not None:
            run_face_detection(app_callback=self._process_and_draw_frame)
            
        else:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            while self.app_master.eye_running:
                ret, frame = cap.read()
                if not ret:
                    break
                if not self._process_and_draw_frame(frame):
                    break
            cap.release()

    def _process_and_draw_frame(self, frame):
        from PIL import Image, ImageTk
        import cv2

        if not self.app_master.eye_running or self.eye_switch.get() == 0:
            self.video_label.configure(image="", text=self.text_bundle["cam_offline"])
            self.video_label.image = None
            self.video_label.pack(fill="none", expand=True, pady=40)
            return False

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            resized_img = pil_img.resize((420, 200), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(image=resized_img)
            
            if self.app_master.eye_running and self.eye_switch.get() == 1:
                self.video_label.configure(image=tk_img, text="")
                self.video_label.image = tk_img  
                self.video_label.pack(fill="both", expand=True, padx=0, pady=0)
                return True
            else:
                return False
        except Exception as e:
            print(f"Frame translation rendering failure anomaly: {e}")
            return False
        
    def _restart_eye_thread(self):
        if self.eye_switch.get() == 1:
            print(">>> [Hot-Reload] Old thread dropped safely. Launching new engine thread now...")
            self.app_master.eye_running = True
            self.eye_thread = threading.Thread(target=self._camera_hardware_pipeline, daemon=True)
            self.eye_thread.start()

    def _bg_voice_loop(self):
        print(">>> [Voice Thread] Connected to Microphone Stream. Listening...")
        while self.app_master.voice_running:
            time.sleep(2)