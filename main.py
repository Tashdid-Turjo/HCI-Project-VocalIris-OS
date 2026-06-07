# For OfflineDesktop Application Creation
# The controller script that runs the sidebar and launches the app

import customtkinter as ctk
from ui.settings_page import SettingsPage
from ui.home_page import HomePage

class VocalIrisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Main Window Dimensions & Title
        self.title("VocalIris OS - Desktop Client")
        self.geometry("1000x600")
        
        # Ensure the app starts in Dark Mode by default
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 2. Layout Grid Configuration (1 Row, 2 Columns)
        # Column 0 = Sidebar (Fixed width), Column 1 = Content (Expands to fill screen)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 3. Create the Left Sidebar Panel
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Pushes anything below down

        # Sidebar Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="VocalIris OS", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # 4. Add the 4 Major Sidebar Buttons
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

        # 5. Create the Right Content Panel (The Stage)
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Display a temporary landing label inside the content panel
        self.page_title_label = ctk.CTkLabel(
            self.content_frame, 
            text="Welcome to VocalIris OS", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.page_title_label.pack(pady=50)

    # 6. The Page Switching Router Function
    def switch_page(self, page_name):
        # Clear the old screen items
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Router evaluations
        if page_name == "Home":
            self.active_page = HomePage(self.content_frame)
            self.active_page.pack(fill="both", expand=True)
            
        elif page_name == "Settings":
            self.active_page = SettingsPage(self.content_frame)
            self.active_page.pack(fill="both", expand=True)
            
        else:
            # Fallback text placeholder for Profile and Help pages
            self.page_title_label = ctk.CTkLabel(
                self.content_frame, 
                text=f"{page_name} View Layout Placeholder", 
                font=ctk.CTkFont(size=24, weight="bold")
            )
            self.page_title_label.pack(pady=20)
            
        print(f"Switched panel router state to: {page_name}")

# Run the Application
if __name__ == "__main__":
    app = VocalIrisApp()
    app.mainloop()