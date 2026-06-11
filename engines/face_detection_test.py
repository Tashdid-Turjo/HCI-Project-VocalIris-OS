import cv2
import mediapipe as mp
import pyautogui
import time
import os
import queue
import sys
import json
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Optimize cursor translation responsiveness by eliminating framework delay limits
pyautogui.PAUSE = 0


# =================================================================
# 1. FACE DETECTION & EYE TRACKING ENGINE
# =================================================================
def run_face_detection(app_callback):
    """
    Wraps the primary face detection and eye tracking engine.
    Feeds frames back to the custom UI canvas instead of opening cv2.imshow.
    """
    # Setup the Task Base (Patched dynamically for standalone .exe execution compatibility)
    if getattr(sys, 'frozen', False):
        # Running inside the compiled PyInstaller .exe bundle context
        base_path = sys._MEIPASS
    else:
        # Running as a loose script inside your development repository directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       
    model_path = os.path.join(base_path, 'face_landmarker.task')


    # Read the model file directly into memory as a binary buffer
    try:
        with open(model_path, 'rb') as f:
            model_buffer = f.read()
    except Exception as e:
        print(f"[ERROR] Loading model file at {model_path}: {e}")
        return


    base_options = python.BaseOptions(model_asset_buffer=model_buffer)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)


    # Setup Camera (Dynamic Fallback Scan Loop for USB/OBS Virtual Cams)
    cam = None
    for index in [0, 1, 2, 3]:
        print(f"[Camera Sync] Attempting to hook into device index: {index} via DirectShow...")
        test_cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
       
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret:
                print(f">>> [Success] Camera engine successfully bound to Index {index}!")
                cam = test_cap
                break
            else:
                test_cap.release()
        else:
            test_cap.release()


    if cam is None:
        print(">>> [CRITICAL] No active hardware cameras detected on indexes 0-3. Attempting default...")
        cam = cv2.VideoCapture(0)


    screen_w, screen_h = pyautogui.size()


    # Variables for manual mouse movement detection overrides
    last_mouse_x, last_mouse_y = pyautogui.position()
    last_manual_move_time = 0


    if not cam.isOpened():
        print("Error: Could not open camera framework entirely.")
        return


    print("VocalIris OS Engine: Face Tracking Loop Engaged.")


    # Loop state flag to completely prevent un-killable background zombie thread cycles
    is_ui_active = True


    while cam.isOpened() and is_ui_active:
        success, frame = cam.read()
        if not success:
            # Safely verify if interface application loop was broken during dropframe events
            is_ui_active = app_callback(frame) if 'frame' in locals() else True
            continue


        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)


        current_mouse_x, current_mouse_y = pyautogui.position()
        if abs(current_mouse_x - last_mouse_x) > 5 or abs(current_mouse_y - last_mouse_y) > 5:
            last_manual_move_time = time.time()


        # Process Landmarks & Translate Iris Data into Pixel Offsets
        if detection_result and detection_result.face_landmarks:
            if time.time() - last_manual_move_time > 1.0:
                landmarks = detection_result.face_landmarks[0]
                iris_point = landmarks[474]  # High-fidelity center point index tracker
               
                mouse_x = int(iris_point.x * screen_w)
                mouse_y = int(iris_point.y * screen_h)
               
                pyautogui.moveTo(mouse_x, mouse_y, _pause=False)
                last_mouse_x, last_mouse_y = mouse_x, mouse_y
            else:
                last_mouse_x, last_mouse_y = current_mouse_x, current_mouse_y


        # Forward current video buffer matrix back to the UI framework hook
        is_ui_active = app_callback(frame)


    cam.release()
    print(">>> [Eye Thread] Face Tracking hardware pipeline dropped safely.")




# =================================================================
# 2. VOICE CONTROL LISTENER ENGINE (SOUNDDEVICE + VOSK)
# =================================================================
audio_queue = queue.Queue()


def _audio_callback(indata, frames, time_info, status):
    """Callback listener that intercepts audio buffers and safely ensures they are Mono for Vosk."""
    if status:
        print(f"Hardware Stream Status Alert: {status}", file=sys.stderr)
   
    try:
        # indata has a shape of (frames, channels).
        # If forced to open in Stereo (2 channels), extract only the left channel to keep it Mono for Vosk.
        if indata.shape[1] > 1:
            mono_data = indata[:, 0].copy()
            audio_queue.put(mono_data.tobytes())
        else:
            audio_queue.put(indata.tobytes())
    except Exception as e:
        print(f"[Callback Error] Failed to process audio buffer: {e}", file=sys.stderr)


def run_voice_recognition(app_master):
    """
    Listens for specialized vocal parameters in a concurrent daemon thread pool.
    Directly binds command keywords to system mouse and scroll actions using Vosk offline arrays.
    """
    print(">>> [Voice Thread] Resolving dynamic path structures for Vosk...")
   
    # Resolve the accurate runtime path context (Local workspace vs compiled .exe bundle)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       
    model_path = os.path.join(base_path, 'model')
    print(f"[Diagnostic] Targeting Vosk resource mapping folder at: {model_path}")
   
    print(">>> [Voice Thread] Loading Vosk Language Model into memory matrix...")
    try:
        model = Model(model_path)
    except Exception as e:
        print(f"\n[FATAL ERROR] Failed to load Vosk model: {e}")
        app_master.voice_running = False
        return


    # -------------------------------------------------------------
    # DYNAMIC HARDWARE AUDIO PROBING LOOP (ELIMINATES MME ERROR 11)
    # -------------------------------------------------------------
    print(">>> [Voice Thread] Entering Audio Hardware Matrix Probe...")
    try:
        device_info = sd.query_devices(kind='input')
        native_rate = int(device_info['default_samplerate'])
        print(f"[Probe] Default Microphone: '{device_info['name']}'")
        print(f"[Probe] Detected Native Hardware Rate: {native_rate}Hz")
    except Exception as e:
        print(f"[Probe Warning] Could not scan default hardware profiles: {e}")
        native_rate = 44100


    # Ordered list of configurations to test against strict Windows drivers
    configs_to_test = [
        {"rate": native_rate, "channels": 1, "desc": "Native Hardware Rate (Mono)"},
        {"rate": native_rate, "channels": 2, "desc": "Native Hardware Rate (Stereo Fallback)"},
        {"rate": 16000, "channels": 1, "desc": "Standard Vosk Rate (Mono)"},
        {"rate": 44100, "channels": 1, "desc": "Fallback 44.1kHz (Mono)"},
        {"rate": 48000, "channels": 1, "desc": "Fallback 48kHz (Mono)"}
    ]


    stream = None
    chosen_rate = 16000


    # Cycle through options until the Windows Audio subsystem signs off on a driver line
    for config in configs_to_test:
        print(f" -> Testing Driver Matrix: {config['desc']} at {config['rate']}Hz...")
        try:
            stream = sd.InputStream(
                samplerate=config['rate'],
                blocksize=2048,
                dtype="int16",      # Handled automatically via high-level conversion layer
                channels=config['channels'],
                callback=_audio_callback
            )
            chosen_rate = config['rate']
            print(f"====> [SUCCESS] Audio channel secured using configuration: {config['desc']}!")
            break
        except Exception as err:
            print(f"   [Rejected Configuration]: {err}")


    if stream is None:
        print("\n[FATAL SYSTEM CRASH] Windows completely blocked all audio driver configurations.")
        app_master.voice_running = False
        return


    # Dynamically match the Vosk Recognizer frequency mapping directly to the working hardware channel rate
    recognizer = KaldiRecognizer(model, chosen_rate)
    print(f">>> [Voice Thread] Vosk Speech Analytics synchronized perfectly at {chosen_rate}Hz.")


    # -------------------------------------------------------------
    # CORE PROCESSING STREAM LOOP
    # -------------------------------------------------------------
    with stream:
        print(">>> [Voice Thread] Active Microphone Listener Channels Open and Ready.")
       
        while app_master.voice_running:
            try:
                # Thread-safe buffer pull out of stream sequence queue
                data = audio_queue.get(timeout=0.5)
               
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    _process_voice_command(result, app_master)
                else:
                    _ = recognizer.PartialResult()
                   
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Voice Engine Loop Anomaly]: {e}")
                break


    print(">>> [Voice Thread] Microphone listener context streams safely dropped.")


def _process_voice_command(json_result, app_master):
    """
    Parses structural JSON evaluation blocks emitted by the local engine
    and handles downstream system command routing logic.
    """
    try:
        res_dict = json.loads(json_result)
        text = res_dict.get("text", "").lower().strip()
       
        if text:
            print(f"[Voice Command Caught]: '{text}'")
           
            # --- PARSED TEXT TRANSFORMATION MACRO TRIGGERS ---
            if "double click" in text:
                print("--> Executing action: DOUBLE CLICK")
                pyautogui.doubleClick()


            elif "single click" in text or "left click" in text:
                print("--> Executing action: SINGLE CLICK")
                pyautogui.click()


            elif "right click" in text:
                print("--> Executing action: RIGHT CLICK")
                pyautogui.rightClick()


            elif "scroll up" in text:
                print("--> Executing action: SCROLL UP")
                pyautogui.scroll(300)   # Positive integer to scroll upward


            elif "scroll down" in text:
                print("--> Executing action: SCROLL DOWN")
                pyautogui.scroll(-300)  # Negative integer to scroll downward
            # --------------------------------------------------
           
    except Exception as e:
        print(f"Failed to compile raw vocal text processing indices: {e}")