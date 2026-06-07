import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    # Update 1: Add 'app_instance' to the parameter list here
    def __init__(self, parent, app_instance):
        # Initialize this view as a frame nested inside our main window container
        super().__init__(parent, fg_color="transparent")
        
        # Update 2: Save the master application connection securely
        self.app_master = app_instance
        
        # 1. Page Header Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="App Settings Layout", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 30), anchor="w", padx=20)

        # ==========================================
        # CONTROL 1: DARK / LIGHT MODE SWITCH
        # ==========================================
        self.theme_label = ctk.CTkLabel(self, text="Appearance Theme:", font=ctk.CTkFont(size=14))
        self.theme_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Dropdown option box matching CustomTkinter parameters
        self.theme_dropdown = ctk.CTkOptionMenu(
            self, 
            values=["Dark", "Light", "System"],
            command=self.change_theme_action
        )
        self.theme_dropdown.pack(anchor="w", padx=20, pady=(0, 20))
        
        # PRE-POPULATE: Read from our JSON instead of hardcoding "Dark"
        saved_theme = self.app_master.settings["theme"].capitalize()
        self.theme_dropdown.set(saved_theme)

        # ==========================================
        # CONTROL 2: LANGUAGE SELECTOR
        # ==========================================
        self.lang_label = ctk.CTkLabel(self, text="Language Selection:", font=ctk.CTkFont(size=14))
        self.lang_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.lang_dropdown = ctk.CTkOptionMenu(
            self, 
            values=["English", "Bengali"],
            command=self.change_language_action # Added command pipeline
        )
        self.lang_dropdown.pack(anchor="w", padx=20, pady=(0, 20))
        
        # PRE-POPULATE: Set value from JSON
        self.lang_dropdown.set(self.app_master.settings["language"])

        # ==========================================
        # CONTROL 3: FONT SIZE CONFIGURATION (SLIDER)
        # ==========================================
        self.font_label = ctk.CTkLabel(self, text="Application Font Size Scaling:", font=ctk.CTkFont(size=14))
        self.font_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.font_slider = ctk.CTkSlider(
            self, 
            from_=12, 
            to=24, 
            number_of_steps=6,
            command=self.change_font_action # Added command pipeline
        )
        self.font_slider.pack(anchor="w", padx=20, pady=(0, 20))
        
        # PRE-POPULATE: Position slider pin from JSON configuration
        self.font_slider.set(self.app_master.settings["font_size"])

        # ==========================================
        # CONTROL 4: POPUP NOTIFICATION TRIGGER (CHECKBOX)
        # ==========================================
        self.popup_checkbox = ctk.CTkCheckBox(
            self, 
            text="Show pop-up message alert when a voice command is recognized",
            command=self.toggle_popup_action # Added command pipeline
        )
        self.popup_checkbox.pack(anchor="w", padx=20, pady=(20, 10))
        
        # PRE-POPULATE: Select or Deselect checkbox based on saved boolean flag
        if self.app_master.settings["show_popups"]:
            self.popup_checkbox.select()
        else:
            self.popup_checkbox.deselect()

    # ==========================================
    # DATA PIPELINE BACK TO INTERACTIVE ACTION SAVE METHODS
    # ==========================================
    def change_theme_action(self, selected_theme):
        ctk.set_appearance_mode(selected_theme.lower())
        # Tell main.py to save the change to the JSON disk
        self.app_master.update_setting("theme", selected_theme.lower())

    def change_language_action(self, selected_lang):
        self.app_master.update_setting("language", selected_lang)

    def change_font_action(self, slider_val):
        self.app_master.update_setting("font_size", int(slider_val))

    def toggle_popup_action(self):
        is_checked = bool(self.popup_checkbox.get())
        self.app_master.update_setting("show_popups", is_checked)