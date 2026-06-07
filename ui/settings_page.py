import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent):
        # Initialize this view as a frame nested inside our main window container
        super().__init__(parent, fg_color="transparent")
        
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
        # Default the selection visual state to match our default setup
        self.theme_dropdown.set("Dark")

        # ==========================================
        # CONTROL 2: LANGUAGE SELECTOR
        # ==========================================
        self.lang_label = ctk.CTkLabel(self, text="Language Selection:", font=ctk.CTkFont(size=14))
        self.lang_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.lang_dropdown = ctk.CTkOptionMenu(self, values=["English", "Bengali"])
        self.lang_dropdown.pack(anchor="w", padx=20, pady=(0, 20))

        # ==========================================
        # CONTROL 3: FONT SIZE CONFIGURATION (SLIDER)
        # ==========================================
        self.font_label = ctk.CTkLabel(self, text="Application Font Size Scaling:", font=ctk.CTkFont(size=14))
        self.font_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.font_slider = ctk.CTkSlider(self, from_=12, to=24, number_of_steps=6)
        self.font_slider.pack(anchor="w", padx=20, pady=(0, 20))
        self.font_slider.set(14) # Default slider pinpoint value

        # ==========================================
        # CONTROL 4: POPUP NOTIFICATION TRIGGER (CHECKBOX)
        # ==========================================
        self.popup_checkbox = ctk.CTkCheckBox(
            self, 
            text="Show pop-up message alert when a voice command is recognized"
        )
        self.popup_checkbox.pack(anchor="w", padx=20, pady=(20, 10))

    # Real-time Theme Modification Function
    def change_theme_action(self, selected_theme):
        # Convert choice text directly to the framework method signature lowercase
        ctk.set_appearance_mode(selected_theme.lower())
        print(f"Theme framework color set dynamically to: {selected_theme}")