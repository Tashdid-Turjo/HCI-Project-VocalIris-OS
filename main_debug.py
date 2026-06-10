# =================================================================
# VocalIris OS - Standalone Diagnostic Debug Launcher
# This file forces a background command console window to open
# alongside the UI wrapper to catch tracking pipeline logs.
# =================================================================

from main import VocalIrisApp

if __name__ == "__main__":
    print("[Debug Environment] Booting VocalIris App Client Engine...")
    print("[Debug Environment] Standard I/O Pipe streaming to this console window.\n")
    
    # Explicitly instantiate and kick off your main CustomTkinter window loop
    app = VocalIrisApp()
    app.mainloop()