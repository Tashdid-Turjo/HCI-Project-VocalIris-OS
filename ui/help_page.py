import customtkinter as ctk
import webbrowser

class HelpPage(ctk.CTkFrame):
    # Added 'app_instance' parameter here to connect language selection flags
    def __init__(self, parent, app_instance):
        super().__init__(parent, fg_color="transparent")
        
        self.app_master = app_instance
        self.current_lang = self.app_master.settings.get("language", "English")
        
        # Extract base font scale factor safely as an integer
        base_font_size = int(self.app_master.settings.get("font_size", 14))

        # =================================================================
        # SYSTEM TROUBLESHOOTING DOCUMENTATION LOCALIZATION (TEXT BLOCKS)
        # =================================================================
        help_guide_en = (
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

        help_guide_bn = (
            "===========================================================\n"
            "                     সিস্টেম ট্রাবলশুটিং গাইড                   \n"
            "===========================================================\n\n"
            "১. হার্ডওয়্যার ওয়েব-ক্যামেরা সমস্যা:\n"
            "   • নিশ্চিত করুন যে অন্য কোনো বাহ্যিক প্রোগ্রাম (Zoom, Discord, Browser) আপনার\n"
            "     ওয়েবক্যামের ইনপুট ফ্রেম বাফারটি লক করে রাখেনি।\n"
            "   • যদি আই-সেন্টারিং অস্থির মনে হয়, তবে ঘরের চারপাশের আলো সমান রাখুন।\n"
            "     পেছনের তীব্র আলো চোখের ডিটেকশন ট্র্যাকিংয়ে সমস্যা তৈরি করে।\n\n"
            "২. মাইক্রোফোন / স্পিচ সমস্যা:\n"
            "   • ভয়েস রিকগনিশন লেটেন্সি বৃদ্ধি পেলে, অডিও বাফার ক্লিয়ার করতে 'ভয়েস সার্ভিস\n"
            "     লিসেনার' সুইচটি একবার অফ করে পুনরায় অন করুন।\n"
            "   • আপনার ডিফল্ট রেকর্ডিং প্যারামিটারগুলি একটি সঠিক ইনপুট স্যাম্পলিং ফ্রিকোয়েন্সিতে টিউন করা আছে কিনা তা যাচাই করুন।\n\n"
            "৩. ক্যালিব্রেশন রিসেট প্রক্রিয়া:\n"
            "   • যদি মাউস কার্সার স্ক্রিনের বাইরে চলে যায় বা ড্রিফট করতে শুরু করে,\n"
            "     তবে অবিলম্বে হোম ড্যাশবোর্ডে ফিরে যান এবং একটি নতুন ক্যালিব্রেশন রান চালু করুন।\n\n"
            "-----------------------------------------------------------\n"
            "অ্যাপ্লিকেশন ফ্রেমওয়ার্ক রিলিজ: ভোকালআইরিস ডেক্সটপ ক্লায়েন্ট v১.০.০ (অফলাইন মোড)"
        )

        # ==========================================
        # ELEMENT-BY-ELEMENT TRANSLATION DICTIONARY
        # ==========================================
        self.translations = {
            "English": {
                "title": "Help & System Support",
                "doc_header": "VocalIris OS Operating Documentation & Logs",
                "discord_lbl": "Need live assistance? For reaching out to us, communicate with the official Discord server:",
                "discord_btn": "Join Discord Server",
                "guide_text": help_guide_en
            },
            "Bangla": {
                "title": "হেল্প এবং সিস্টেম সাপোর্ট",
                "doc_header": "ভোকালআইরিস ওএস অপারেটিং ডকুমেন্টেশন এবং লগ",
                "discord_lbl": "সরাসরি সহায়তার প্রয়োজন? আমাদের সাথে যোগাযোগের জন্য অফিশিয়াল ডিসকর্ড সার্ভারে যুক্ত হোন:",
                "discord_btn": "ডিসকর্ড সার্ভারে যুক্ত হোন",
                "guide_text": help_guide_bn
            }
        }

        # Select the active text translation bundle
        text_bundle = self.translations.get(self.current_lang, self.translations["English"])
        
        # Page Title Header (Proportional Scaling: Base + 10)
        self.title_label = ctk.CTkLabel(
            self, text=text_bundle["title"], 
            font=ctk.CTkFont(size=base_font_size + 10, weight="bold")
        )
        self.title_label.pack(pady=(10, 20), anchor="w", padx=20)

        # Documentation Summary Card Container
        self.doc_card = ctk.CTkFrame(self)
        self.doc_card.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Documentation Card Subheader (Proportional Scaling: Base + 2)
        self.doc_header = ctk.CTkLabel(
            self.doc_card, text=text_bundle["doc_header"], 
            font=ctk.CTkFont(size=base_font_size + 2, weight="bold")
        )
        self.doc_header.pack(anchor="w", padx=20, pady=15)

        # Large informational readout frame text box (Passes direct scaling to font configuration)
        self.help_text_box = ctk.CTkTextbox(
            self.doc_card, 
            activate_scrollbars=True,
            font=ctk.CTkFont(family="Courier", size=base_font_size)
        )
        self.help_text_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Insert translation bundle guide text string
        self.help_text_box.insert("0.0", text_bundle["guide_text"])
        self.help_text_box.configure(state="disabled") # Set text box to read-only mode

        # =================================================================
        # DISCORD COMMUNITY SUPPORT SECTION
        # =================================================================
        self.support_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.support_frame.pack(fill="x", padx=20, pady=(10, 10))

        # Support Label Text (Proportional Scaling: Base size matching standard guidelines)
        self.discord_label = ctk.CTkLabel(
            self.support_frame, 
            text=text_bundle["discord_lbl"],
            font=ctk.CTkFont(size=base_font_size),
            wraplength=600, justify="left" # Added protection for long Bengali lines
        )
        self.discord_label.pack(side="left", padx=(5, 15))

        # Interactive Discord Button (Applies proportional base size text)
        self.btn_discord = ctk.CTkButton(
            self.support_frame, 
            text=text_bundle["discord_btn"], 
            fg_color="#5865F2",       # Discord's official Blurple color brand hex
            hover_color="#4752C4",
            width=150,
            command=self.open_discord_link,
            font=ctk.CTkFont(size=base_font_size)
        )
        self.btn_discord.pack(side="right", padx=5)

    def open_discord_link(self):
        """Launches the user's default browser pointing directly to the support server link."""
        discord_url = "https://discord.gg/R3nqaffQ"
        webbrowser.open_new_tab(discord_url)