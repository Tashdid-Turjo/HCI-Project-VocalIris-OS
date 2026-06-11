# For OfflineDesktop Application Creation
# The controller script that runs the sidebar and launches the app

import os
import json
import sys
import customtkinter as ctk
from ui.home_page import HomePage
from ui.settings_page import SettingsPage
from ui.profile_page import ProfilePage
from ui.help_page import HelpPage

def get_asset_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class VocalIrisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ==========================================
        # 1. TRACKING LIFETIME APPLICATION STATES
        # ==========================================
        self.active_page_name = None  # Tracks which view is actively open
        
        # Thread status flags stored here so they survive view changes
        self.voice_running = False
        self.eye_running = False

        self.config_filename = "config.json"
        self.default_settings = {
            "theme": "dark",
            "language": "English",
            "font_size": 14,
            "show_popups": True,
            "behavioral_profile": "browsing"
        }
        self.settings = self.load_configuration()

        # ==========================================
        # LOCALIZATION FOR SIDEBAR MAPPING
        # ==========================================
        self.sidebar_translations = {
            "English": {
                "home": "Home",
                "settings": "App Settings",
                "profile": "Profile",
                "help": "Help & Supports"
            },
            "Bangla": {
                "home": "হোম",
                "settings": "অ্যাপ সেটিংস",
                "profile": "প্রোফাইল",
                "help": "হেল্প এবং সাপোর্ট"
            }
        }

        # ==========================================
        # 2. MAIN WINDOW CONFIGURATION
        # ==========================================
        self.title("VocalIris OS - Desktop Client")
        self.geometry("1000x600")
        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme("blue")

        # CHANGE THIS LINE TO USE THE HELPER FUNCTION:
        self.iconbitmap(get_asset_path("logo.ico"))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 3. SIDEBAR NAVIGATION PANEL
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        # Adjust row weights to make room for your logo image
        self.sidebar_frame.grid_rowconfigure(6, weight=1) 

        # 1. LOAD THE SIDEBAR PNG IMAGE (Using our asset helper)
        from PIL import Image  # Ensure PIL Image is available
        
        self.sidebar_logo_image = ctk.CTkImage(
            light_image=Image.open(get_asset_path("logo.png")),
            dark_image=Image.open(get_asset_path("logo.png")),
            size=(120, 120)  # You can adjust this size (width, height) to make it look perfect!
        )

        # 2. RENDER THE TEXT HEADER (Font size will be managed by update_sidebar_languages)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="VocalIris OS")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        # 3. NEW: RENDER THE LOGO IMAGE DIRECTLY UNDERNEATH THE TEXT
        self.logo_image_label = ctk.CTkLabel(
            self.sidebar_frame, text="", image=self.sidebar_logo_image
        )
        self.logo_image_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # 4. SHIFT THE BUTTON ROWS DOWN BY 1 TO ACCOMMODATE THE LOGO IMAGE
        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="", command=lambda: self.switch_page("Home"))
        self.btn_home.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="", command=lambda: self.switch_page("Settings"))
        self.btn_settings.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_profile = ctk.CTkButton(self.sidebar_frame, text="", command=lambda: self.switch_page("Profile"))
        self.btn_profile.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_help = ctk.CTkButton(self.sidebar_frame, text="", command=lambda: self.switch_page("Help"))
        self.btn_help.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # Set initial sidebar translation labels and font sizes
        self.update_sidebar_languages()

        # Dynamic Content Panel
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.switch_page("Home")

    def load_configuration(self):
        if os.path.exists(self.config_filename):
            try:
                with open(self.config_filename, "r") as file:
                    return json.load(file)
            except Exception:
                return self.default_settings.copy()
        else:
            try:
                with open(self.config_filename, "w") as file:
                    json.dump(self.default_settings, file, indent=4)
            except Exception:
                pass
            return self.default_settings.copy()

    def update_setting(self, key, value):
        self.settings[key] = value
        try:
            with open(self.config_filename, "w") as file:
                json.dump(self.settings, file, indent=4)
        except Exception:
            pass
        
        # If language parameter updates, immediately synchronize navigation components
        if key == "language":
            self.update_sidebar_languages()
            
        # Hot-reload font changes across the sidebar and current active view frame instantly
        elif key == "font_size":
            self.update_sidebar_languages()
            if self.active_page_name:
                self.switch_page(self.active_page_name, force_reload=True)

    def update_sidebar_languages(self):
        """Redraws the sidebar UI strings and scales fonts dynamically using configuration states."""
        lang = self.settings.get("language", "English")
        base_size = int(self.settings.get("font_size", 14))
        bundle = self.sidebar_translations.get(lang, self.sidebar_translations["English"])
        
        # Apply relative scale sizing factors
        self.logo_label.configure(font=ctk.CTkFont(size=base_size + 6, weight="bold"))
        
        self.btn_home.configure(text=bundle["home"], font=ctk.CTkFont(size=base_size))
        self.btn_settings.configure(text=bundle["settings"], font=ctk.CTkFont(size=base_size))
        self.btn_profile.configure(text=bundle["profile"], font=ctk.CTkFont(size=base_size))
        self.btn_help.configure(text=bundle["help"], font=ctk.CTkFont(size=base_size))

    # ==========================================
    # SMART ROUTER CONTROLLER ENGINE
    # ==========================================
    def switch_page(self, page_name, force_reload=False):
        # Allow bypass of the identical-page blocking mechanism if a force_reload is needed
        if self.active_page_name == page_name and not force_reload:
            print(f"Ignored duplicate click for: {page_name}")
            return

        # Record this new page as the current active view
        self.active_page_name = page_name

        # Wipe the dynamic panel content clean
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if page_name == "Home":
            self.active_page = HomePage(self.content_frame, app_instance=self)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Settings":
            self.active_page = SettingsPage(self.content_frame, app_instance=self)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Profile":
            self.active_page = ProfilePage(self.content_frame, app_instance=self)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Help":
            self.active_page = HelpPage(self.content_frame, app_instance=self)
            self.active_page.pack(fill="both", expand=True)
            
        print(f"Switched panel router state to: {page_name}")

# Run the Application
if __name__ == "__main__":
    app = VocalIrisApp()
    app.mainloop()