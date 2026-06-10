import customtkinter as ctk
import webbrowser

class HelpPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Page Title Header
        self.title_label = ctk.CTkLabel(
            self, text="Help & System Support", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(10, 20), anchor="w", padx=20)

        # Documentation Summary Card Container
        self.doc_card = ctk.CTkFrame(self)
        self.doc_card.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.doc_header = ctk.CTkLabel(
            self.doc_card, text="VocalIris OS Operating Documentation & Logs", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.doc_header.pack(anchor="w", padx=20, pady=15)

        # Large informational readout frame text box
        self.help_text_box = ctk.CTkTextbox(self.doc_card, activate_scrollbars=True)
        self.help_text_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        help_guide = (
            "===========================================================\n"
            "                 SYSTEM TROUBLESHOOTING GUIDE              \n"
            "===========================================================\n\n"
            "1. HARDWARE Web-Camera Failures:\n"
            "   • Check that no external program (Zoom, Discord, Browser) is locking\n"
            "     the local webcam input frame buffer.\n"
            "   • If eyeball centering feels unstable, ensure your space has even\n"
            "     ambient room lighting. Strong backlighting will cause eye detection tracking anomalies.\n\n"
            "2. MICROPHONE / SPEECH Failures:\n"
            "   • If voice recognition latency increases, toggle the 'Voice Service\n"
            "     Listener' switch off and back on again to flush the audio buffer streams.\n"
            "   • Verify that your default native recording parameters are tuned to an operational input sampling frequency.\n\n"
            "3. CALIBRATION Reset Procedures:\n"
            "   • If mouse cursor drift begins expanding across monitor coordinate scales,\n"
            "     return immediately to the Home Dashboard pane and launch a clean calibration execution run.\n\n"
            "-----------------------------------------------------------\n"
            "Application Framework Release: VocalIris Desktop Client v1.0.0 (Offline Mode Built)"
        )
        self.help_text_box.insert("0.0", help_guide)
        self.help_text_box.configure(state="disabled") # Set text box to read-only mode

        # =================================================================
        # NEW: DISCORD COMMUNITY SUPPORT SECTION
        # =================================================================
        self.support_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.support_frame.pack(fill="x", padx=20, pady=(10, 10))

        # Support Label Text
        self.discord_label = ctk.CTkLabel(
            self.support_frame, 
            text="Need live assistance? For reaching out to us, communicate with the official Discord server:",
            font=ctk.CTkFont(size=13)
        )
        self.discord_label.pack(side="left", padx=(5, 15))

        # Interactive Discord Button
        self.btn_discord = ctk.CTkButton(
            self.support_frame, 
            text="Join Discord Server", 
            fg_color="#5865F2",       # Discord's official Blurple color brand hex
            hover_color="#4752C4",
            width=150,
            command=self.open_discord_link
        )
        self.btn_discord.pack(side="right", padx=5)

    def open_discord_link(self):
        """Launches the user's default browser pointing directly to the support server link."""
        discord_url = "https://discord.gg/R3nqaffQ"
        webbrowser.open_new_tab(discord_url)