import customtkinter as ctk

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Page Title Header
        self.title_label = ctk.CTkLabel(
            self, text="User Operating Profiles", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 30), anchor="w", padx=20)

        # ==========================================
        # CARD 1: OPERATION PRESET MODES (RADIO BUTTONS)
        # ==========================================
        self.mode_card = ctk.CTkFrame(self)
        self.mode_card.pack(fill="x", padx=20, pady=10)

        self.mode_title = ctk.CTkLabel(
            self.mode_card, text="Select System Behavioral Profile", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.mode_title.pack(anchor="w", padx=20, pady=(15, 10))

        # This variable tracks which radio button is active
        self.profile_var = ctk.StringVar(value="browsing")

        self.radio_browsing = ctk.CTkRadioButton(
            self.mode_card, text="Web Browsing Mode (High-Agility Eye Tracking & Gestures)",
            variable=self.profile_var, value="browsing", command=self.sync_profile_mode
        )
        self.radio_browsing.pack(anchor="w", padx=30, pady=10)

        self.radio_reading = ctk.CTkRadioButton(
            self.mode_card, text="Reading Mode (Damped Smooth Cursor & Quick Scrolling Shortcuts)",
            variable=self.profile_var, value="reading", command=self.sync_profile_mode
        )
        self.radio_reading.pack(anchor="w", padx=30, pady=10)

        # ==========================================
        # CARD 2: PORTABILITY & BACKUPS (DATA EXPORT)
        # ==========================================
        self.data_card = ctk.CTkFrame(self)
        self.data_card.pack(fill="x", padx=20, pady=15)

        self.data_title = ctk.CTkLabel(
            self.data_card, text="Data Portability & Migration", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.data_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.data_desc = ctk.CTkLabel(
            self.data_card, 
            text="Export your local eye-calibration matrix values, system preferences, and rules dictionaries into an external setup file to share or back up.",
            text_color="#888888", font=ctk.CTkFont(size=12)
        )
        self.data_desc.pack(anchor="w", padx=20, pady=(0, 15))

        self.export_btn = ctk.CTkButton(
            self.data_card, text="Export User Settings Matrix", 
            command=self.trigger_export_alert
        )
        self.export_btn.pack(anchor="w", padx=20, pady=(0, 15))

    def sync_profile_mode(self):
        print(f"Active behavioral preset swapped to: {self.profile_var.get().upper()} profile mode")

    def trigger_export_alert(self):
        print("Export execution fired! Ready to prompt system file browser dialog saves.")