import customtkinter as ctk

class ProfilePage(ctk.CTkFrame):
    # Added 'app_instance' parameter to check current global language state
    def __init__(self, parent, app_instance):
        super().__init__(parent, fg_color="transparent")
        
        self.app_master = app_instance
        self.current_lang = self.app_master.settings.get("language", "English")

        # ==========================================
        # LOCALIZATION (TRANSLATION) DICTIONARY
        # ==========================================
        self.translations = {
            "English": {
                "title": "User Operating Profiles",
                "mode_title": "Select System Behavioral Profile",
                "radio_browsing": "Web Browsing Mode (High-Agility Eye Tracking & Gestures)",
                "radio_reading": "Reading Mode (Damped Smooth Cursor & Quick Scrolling Shortcuts)",
                "data_title": "Data Portability & Migration",
                "data_desc": "Export your local eye-calibration matrix values, system preferences, and rules dictionaries into an external setup file to share or back up.",
                "export_btn": "Export User Settings Matrix"
            },
            "Bangla": {
                "title": "ব্যবহারকারী অপারেটিং প্রোফাইল",
                "mode_title": "সিস্টেমের আচরণগত প্রোফাইল নির্বাচন করুন",
                "radio_browsing": "ওয়েব ব্রাউজিং মোড (উচ্চ-গতিশীল আই ট্র্যাকিং এবং জেসচার)",
                "radio_reading": "রিডিং মোড (ড্যাম্পড স্মুথ কার্সার এবং কুইক স্ক্রোলিং শর্টকাট)",
                "data_title": "ডেটা পোর্টেবিলিটি এবং মাইগ্রেশন",
                "data_desc": "শেয়ার বা ব্যাকআপ করার জন্য আপনার লোকাল আই-ক্যালিব্রেশন ম্যাট্রিক্স মান, সিস্টেম পছন্দসমূহ এবং নিয়মাবলীর ডিকশনারি একটি এক্সটার্নাল ফাইল হিসেবে এক্সপোর্ট করুন।",
                "export_btn": "ইউজার সেটিংস ম্যাট্রিক্স এক্সপোর্ট করুন"
            }
        }

        # Select the active text translation bundle
        text_bundle = self.translations.get(self.current_lang, self.translations["English"])
        
        # Page Title Header
        self.title_label = ctk.CTkLabel(
            self, text=text_bundle["title"], 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 30), anchor="w", padx=20)

        # ==========================================
        # CARD 1: OPERATION PRESET MODES (RADIO BUTTONS)
        # ==========================================
        self.mode_card = ctk.CTkFrame(self)
        self.mode_card.pack(fill="x", padx=20, pady=10)

        self.mode_title = ctk.CTkLabel(
            self.mode_card, text=text_bundle["mode_title"], 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.mode_title.pack(anchor="w", padx=20, pady=(15, 10))

        # This variable tracks which radio button is active (Pre-populates from config settings)
        saved_profile = self.app_master.settings.get("behavioral_profile", "browsing")
        self.profile_var = ctk.StringVar(value=saved_profile)

        self.radio_browsing = ctk.CTkRadioButton(
            self.mode_card, text=text_bundle["radio_browsing"],
            variable=self.profile_var, value="browsing", command=self.sync_profile_mode
        )
        self.radio_browsing.pack(anchor="w", padx=30, pady=10)

        self.radio_reading = ctk.CTkRadioButton(
            self.mode_card, text=text_bundle["radio_reading"],
            variable=self.profile_var, value="reading", command=self.sync_profile_mode
        )
        self.radio_reading.pack(anchor="w", padx=30, pady=10)

        # ==========================================
        # CARD 2: PORTABILITY & BACKUPS (DATA EXPORT)
        # ==========================================
        self.data_card = ctk.CTkFrame(self)
        self.data_card.pack(fill="x", padx=20, pady=15)

        self.data_title = ctk.CTkLabel(
            self.data_card, text=text_bundle["data_title"], 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.data_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.data_desc = ctk.CTkLabel(
            self.data_card, 
            text=text_bundle["data_desc"],
            text_color="#888888", font=ctk.CTkFont(size=12),
            wraplength=750, justify="left" # Added wrapping to keep long text formatted cleanly
        )
        self.data_desc.pack(anchor="w", padx=20, pady=(0, 15))

        self.export_btn = ctk.CTkButton(
            self.data_card, text=text_bundle["export_btn"], 
            command=self.trigger_export_alert
        )
        self.export_btn.pack(anchor="w", padx=20, pady=(0, 15))

    def sync_profile_mode(self):
        new_profile = self.profile_var.get()
        print(f"Active behavioral preset swapped to: {new_profile.upper()} profile mode")
        # Save change back to global settings dictionary state
        self.app_master.update_setting("behavioral_profile", new_profile)

    def trigger_export_alert(self):
        print("Export execution fired! Ready to prompt system file browser dialog saves.")