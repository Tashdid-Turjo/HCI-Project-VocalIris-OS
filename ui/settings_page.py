import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app_instance):
        super().__init__(parent, fg_color="transparent")
        
        self.app_master = app_instance
        self.current_lang = self.app_master.settings.get("language", "English")
        
        # Extract base font scale factor safely as an integer
        base_font_size = int(self.app_master.settings.get("font_size", 14))

        # ==========================================
        # LOCALIZATION (TRANSLATION) DICTIONARY
        # ==========================================
        self.translations = {
            "English": {
                "title": "App Settings Layout",
                "theme_lbl": "Appearance Theme:",
                "lang_lbl": "Language Selection:",
                "font_lbl": "Application Font Size Scaling:",
                "popup_chk": "Show pop-up message alert when a voice command is recognized",
                "themes": ["Dark", "Light", "System"]
            },
            "Bangla": {
                "title": "অ্যাপ সেটিংস লেআউট",
                "theme_lbl": "অ্যাপিয়ারেন্স থিম (পদ্ধতি):",
                "lang_lbl": "ভাষা নির্বাচন করুন:",
                "font_lbl": "অ্যাপ্লিকেশন ফন্ট সাইজ স্কেলিং:",
                "popup_chk": "ভয়েস কমান্ড সনাক্ত করা হলে পপ-আপ বার্তা প্রদর্শন করুন",
                "themes": ["ডার্ক", "লাইট", "সিস্টেম"]
            }
        }

        # Select the active text translation bundle
        text_bundle = self.translations.get(self.current_lang, self.translations["English"])

        # 1. Page Header Title (Proportional Scaling: Base + 10)
        self.title_label = ctk.CTkLabel(
            self, 
            text=text_bundle["title"], 
            font=ctk.CTkFont(size=base_font_size + 10, weight="bold")
        )
        self.title_label.pack(pady=(10, 30), anchor="w", padx=20)

        # ==========================================
        # CONTROL 1: DARK / LIGHT MODE SWITCH
        # ==========================================
        self.theme_label = ctk.CTkLabel(
            self, 
            text=text_bundle["theme_lbl"], 
            font=ctk.CTkFont(size=base_font_size)
        )
        self.theme_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Display themes based on selected language
        self.theme_dropdown = ctk.CTkOptionMenu(
            self, 
            values=text_bundle["themes"],
            command=self.change_theme_action,
            font=ctk.CTkFont(size=base_font_size),
            dropdown_font=ctk.CTkFont(size=base_font_size)
        )
        self.theme_dropdown.pack(anchor="w", padx=20, pady=(0, 20))
        
        # PRE-POPULATE: Read theme state from config profile
        saved_theme = self.app_master.settings["theme"].lower()
        if self.current_lang == "Bangla":
            if saved_theme == "dark": self.theme_dropdown.set("ডার্ক")
            elif saved_theme == "light": self.theme_dropdown.set("লাইট")
            else: self.theme_dropdown.set("সিস্টেম")
        else:
            self.theme_dropdown.set(saved_theme.capitalize())

        # ==========================================
        # CONTROL 2: LANGUAGE SELECTOR
        # ==========================================
        self.lang_label = ctk.CTkLabel(
            self, 
            text=text_bundle["lang_lbl"], 
            font=ctk.CTkFont(size=base_font_size)
        )
        self.lang_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Scale dropdown button option text
        self.lang_dropdown = ctk.CTkOptionMenu(
            self, 
            values=["English", "Bangla"],
            command=self.change_language_action,
            font=ctk.CTkFont(size=base_font_size),
            dropdown_font=ctk.CTkFont(size=base_font_size)
        )
        self.lang_dropdown.pack(anchor="w", padx=20, pady=(0, 20))
        self.lang_dropdown.set(self.current_lang)

        # ==========================================
        # CONTROL 3: FONT SIZE CONFIGURATION (SLIDER)
        # ==========================================
        # Append live numeric value string next to layout label string for UX transparency
        font_display_text = f"{text_bundle['font_lbl']} ({base_font_size}px)"
        
        self.font_label = ctk.CTkLabel(
            self, 
            text=font_display_text, 
            font=ctk.CTkFont(size=base_font_size)
        )
        self.font_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.font_slider = ctk.CTkSlider(
            self, 
            from_=12, 
            to=24, 
            number_of_steps=6,
            command=self.change_font_action 
        )
        self.font_slider.pack(anchor="w", padx=20, pady=(0, 20))
        self.font_slider.set(base_font_size)

        # ==========================================
        # CONTROL 4: POPUP NOTIFICATION TRIGGER (CHECKBOX)
        # ==========================================
        self.popup_checkbox = ctk.CTkCheckBox(
            self, 
            text=text_bundle["popup_chk"],
            command=self.toggle_popup_action,
            font=ctk.CTkFont(size=base_font_size)
        )
        self.popup_checkbox.pack(anchor="w", padx=20, pady=(20, 10))
        
        if self.app_master.settings["show_popups"]:
            self.popup_checkbox.select()
        else:
            self.popup_checkbox.deselect()

    # ==========================================
    # DATA PIPELINE METHODS
    # ==========================================
    def change_theme_action(self, selected_theme):
        # Convert localized options back to standard string arguments for CustomTkinter backend
        theme_map = {"Dark": "dark", "Light": "light", "System": "system",
                     "ডার্ক": "dark", "লাইট": "light", "সিস্টেম": "system"}
        eng_theme = theme_map.get(selected_theme, "dark")
        
        ctk.set_appearance_mode(eng_theme)
        self.app_master.update_setting("theme", eng_theme)

    def change_language_action(self, selected_lang):
        self.app_master.update_setting("language", selected_lang)
        # Force the router engine to rerun the page constructor context cleanly
        self.app_master.switch_page("Settings", force_reload=True)

    def change_font_action(self, slider_val):
        # Cast value smoothly to an integer step
        int_val = int(slider_val)
        self.app_master.update_setting("font_size", int_val)

    def toggle_popup_action(self):
        is_checked = bool(self.popup_checkbox.get())
        self.app_master.update_setting("show_popups", is_checked)