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
        # 1. LOCAL STORAGE FILE PATH & BLUEPRINT
        # ==========================================
        self.config_filename = "config.json"
        self.default_settings = {
            "theme": "dark",
            "language": "English",
            "font_size": 14,
            "show_popups": True,
            "behavioral_profile": "browsing"
        }
        
        # Load existing configuration or generate the fallback defaults
        self.settings = self.load_configuration()

        # ==========================================
        # 2. MAIN WINDOW CONFIGURATION
        # ==========================================
        self.title("VocalIris OS - Desktop Client")
        self.geometry("1000x600")
        
        # Apply the user's saved theme preference globally immediately on boot
        ctk.set_appearance_mode(self.settings["theme"])
        ctk.set_default_color_theme("blue")

        # Layout Grid (1 Row, 2 Columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 3. SIDEBAR NAVIGATION PANEL
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) 

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="VocalIris OS", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Sidebar Buttons Linked to Router Engine
        self.btn_home = ctk.CTkButton(
            self.sidebar_frame, text="Home", 
            command=lambda: self.switch_page("Home")
        )
        self.btn_home.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self.sidebar_frame, text="App Settings", 
            command=lambda: self.switch_page("Settings")
        )
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_profile = ctk.CTkButton(
            self.sidebar_frame, text="Profile", 
            command=lambda: self.switch_page("Profile")
        )
        self.btn_profile.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_help = ctk.CTkButton(
            self.sidebar_frame, text="Help & Supports", 
            command=lambda: self.switch_page("Help")
        )
        self.btn_help.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # ==========================================
        # 4. DYNAMIC RIGHT CONTENT PANELS
        # ==========================================
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Load the Home page directly as our default landing view
        self.switch_page("Home")

    # ==========================================
    # JSON STORAGE CONTROLLER LOGIC
    # ==========================================
    def load_configuration(self):
        """Reads preferences from the local JSON path or creates it if missing."""
        if os.path.exists(self.config_filename):
            try:
                with open(self.config_filename, "r") as file:
                    data = json.load(file)
                    print("Local preferences file parsed successfully.")
                    return data
            except Exception as e:
                print(f"Error parsing JSON configuration file ({e}). Resetting to default.")
                return self.default_settings.copy()
        else:
            # File missing: write the default blueprint data structure to the drive
            try:
                with open(self.config_filename, "w") as file:
                    json.dump(self.default_settings, file, indent=4)
                print("Fresh config.json file initialized in the parent workspace directory.")
            except Exception as e:
                print(f"Critical workspace error writing JSON file: {e}")
            return self.default_settings.copy()

    def update_setting(self, key, value):
        """Saves a modified parameter to local storage in real-time."""
        self.settings[key] = value
        try:
            with open(self.config_filename, "w") as file:
                json.dump(self.settings, file, indent=4)
            print(f"Saved configuration to disk -> [{key}]: {value}")
        except Exception as e:
            print(f"Failed to commit parameter modification to JSON registry: {e}")

    # ==========================================
    # MULTI-FRAME ROUTER CONTROLLER ENGINE
    # ==========================================
    def switch_page(self, page_name):
        """Wipes the dynamic content card and slots the target layout class on stage."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if page_name == "Home":
            self.active_page = HomePage(self.content_frame)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Settings":
            # Pass 'self' (the app instance) explicitly right here!
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