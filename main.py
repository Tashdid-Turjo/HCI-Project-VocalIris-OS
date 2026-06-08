# For OfflineDesktop Application Creation
# The controller script that runs the sidebar and launches the app

import os
import json
import customtkinter as ctk
from ui.home_page import HomePage
from ui.settings_page import SettingsPage
from ui.profile_page import ProfilePage
from ui.help_page import HelpPage

    
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
        # 2. MAIN WINDOW CONFIGURATION
        # ==========================================
        self.title("VocalIris OS - Desktop Client")
        self.geometry("1000x600")
        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 3. SIDEBAR NAVIGATION PANEL
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="VocalIris OS", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="Home", command=lambda: self.switch_page("Home"))
        self.btn_home.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text="App Settings", command=lambda: self.switch_page("Settings"))
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_profile = ctk.CTkButton(self.sidebar_frame, text="Profile", command=lambda: self.switch_page("Profile"))
        self.btn_profile.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_help = ctk.CTkButton(self.sidebar_frame, text="Help & Supports", command=lambda: self.switch_page("Help"))
        self.btn_help.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

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

    # ==========================================
    # SMART ROUTER CONTROLLER ENGINE
    # ==========================================
    def switch_page(self, page_name):
        # FIX 1: If the user clicks the button for the page already open, ignore it completely!
        if self.active_page_name == page_name:
            print(f"Ignored duplicate click for: {page_name}")
            return

        # Record this new page as the current active view
        self.active_page_name = page_name

        # Wipe the dynamic panel content clean
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if page_name == "Home":
            # Pass self (app instance) so Home can read/write global states
            self.active_page = HomePage(self.content_frame, app_instance=self)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Settings":
            self.active_page = SettingsPage(self.content_frame, app_instance=self)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Profile":
            self.active_page = ProfilePage(self.content_frame)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Help":
            self.active_page = HelpPage(self.content_frame)
            self.active_page.pack(fill="both", expand=True)
            
        print(f"Switched panel router state to: {page_name}")

# Run the Application
if __name__ == "__main__":
    app = VocalIrisApp()
    app.mainloop()