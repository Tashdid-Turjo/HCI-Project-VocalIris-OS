import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import queue
import json
import os
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Setup Thread Safe Communication Queue
voice_queue = queue.Queue()


def voice_callback(indata, frames, time, status):
    """Captures real-time raw audio chunks from microphone input hardware buffer."""
    voice_queue.put(bytes(indata))


def run_voice_recognition(app_instance):
    """
    Launches your Vosk engine listener module cleanly.
    Loops continuously until app_instance.voice_running is set to False.
    """
    # FIX 1: Resolve the dynamic model directory path context for PyInstaller
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       
    VOSK_MODEL_PATH = os.path.join(base_path, "model")
   
    print(f"[Voice Sync] Initializing Acoustic Model from location: {VOSK_MODEL_PATH}")
    try:
        model = Model(VOSK_MODEL_PATH)
    except Exception as e:
        print(f">>> [CRITICAL] Vosk Voice Engine failed to load model: {e}")
        return
       
    rec = KaldiRecognizer(model, 16000, '["click", "select", "double", "right", "close"]')
   
    # Open local audio recording pipe streams
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=voice_callback):
        print("Vosk Voice Engine: Listening to active stream pipeline...")
       
        while app_instance.voice_running:
            try:
                # Use a small timeout so the loop stays active and check if the stop flag is raised
                data = voice_queue.get(timeout=0.5)
            except queue.Empty:
                continue


            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                command = result.get("text", "")
               
                if "click" in command or "select" in command:
                    print("COMMAND EXECUTION -> Left Click")
                    pyautogui.click()
                elif "double" in command:
                    print("COMMAND EXECUTION -> Double Click")
                    pyautogui.doubleClick()
                elif "right" in command:
                    print("COMMAND EXECUTION -> Contextual Right Click")
                    pyautogui.rightClick()


    print(">>> [Voice Thread] Voice tracking hardware engine closed safely.")




def run_eyeball_tracking(app_callback):
    """
    Wraps your high-precision eyeball contour mapping engine.
    Passes frames directly back to your CustomTkinter dashboard framework.
    """
    pyautogui.FAILSAFE = False
   
    # FIX: Bulletproof Binary Buffer Fix for MediaPipe Face Landmarker
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       
    model_path = os.path.join(base_path, 'face_landmarker.task')


    try:
        with open(model_path, 'rb') as f:
            model_buffer = f.read()
    except Exception as e:
        print(f"Error loading model file at {model_path}: {e}")
        return


    base_options = python.BaseOptions(model_asset_buffer=model_buffer)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)


    # =================================================================
    # CALIBRATION & CONFIGURATION STATES
    # =================================================================
    SMOOTH_FACTOR = 0.10  # Slightly smoother movement
    DEADZONE = 3        
    OVERRIDE_THRESHOLD = 15
    RESUME_DELAY = 1.5      


    # These track your real-world resting eye metrics dynamically
    calibrated_center_x = 0.5
    calibrated_center_y = 0.5
    calibration_frames_gathered = 0
    REQUIRED_CALIBRATION_FRAMES = 15


    RIGHT_EYE_CONTOUR = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]


    prev_x, prev_y = pyautogui.position()
    last_manual_move_time = 0


    # Camera Scan Loop
    cam = None
    for index in [0, 1, 2, 3]:
        print(f"[Camera Sync] Attempting to hook into eyeball tracker index: {index} via DirectShow...")
        test_cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
       
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret:
                print(f">>> [Success] Eyeball tracker bound cleanly to Index {index}!")
                cam = test_cap
                break
            else:
                test_cap.release()
        else:
            test_cap.release()


    if cam is None:
        print(">>> [CRITICAL] Eye tracking engine failed fallback scanning. Initializing default...")
        cam = cv2.VideoCapture(0)


    screen_w, screen_h = pyautogui.size()
    print("VocalIris OS Engine: High-Precision Eyeball Tracking Loop Engaged.")
    print("[Calibration Mode] Please look at the center of your monitor for 2 seconds...")


    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            continue


        frame = cv2.flip(frame, 1)
        img_h, img_w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)


        # Manual Override Check
        actual_x, actual_y = pyautogui.position()
        if abs(actual_x - prev_x) > OVERRIDE_THRESHOLD or abs(actual_y - prev_y) > OVERRIDE_THRESHOLD:
            last_manual_move_time = time.time()
            prev_x, prev_y = actual_x, actual_y


        time_since_manual = time.time() - last_manual_move_time


        if detection_result and detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
           
            iris = landmarks[474]
            l_corner, r_corner = landmarks[33], landmarks[133]
            t_edge, b_edge = landmarks[159], landmarks[145]


            # 1. Calculate the raw relative ratios inside the eye box boundaries
            raw_rel_x = (iris.x - l_corner.x) / (r_corner.x - l_corner.x)
            raw_rel_y = (iris.y - t_edge.y) / (b_edge.y - t_edge.y)


            # 2. RUNTIME AUTO-CALIBRATION MATRIX
            if calibration_frames_gathered < REQUIRED_CALIBRATION_FRAMES:
                # Accumulate the running center data while the user looks at the screen
                if calibration_frames_gathered == 0:
                    calibrated_center_x = raw_rel_x
                    calibrated_center_y = raw_rel_y
                else:
                    calibrated_center_x = (calibrated_center_x + raw_rel_x) / 2
                    calibrated_center_y = (calibrated_center_y + raw_rel_y) / 2
               
                calibration_frames_gathered += 1
                # Put a temporary message on the UI frame to show it's calibrating
                cv2.putText(frame, "Calibrating... Look Center", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
               
            else:
                # 3. USE CALIBRATED OFFSETS
                # Find how far your eye shifts relative to YOUR specific resting center point
                offset_x = raw_rel_x - calibrated_center_x
                offset_y = raw_rel_y - calibrated_center_y


                # GAIN CONTROLS: Normalized tracking gears
                GAIN_X = 6.5
                GAIN_Y = 5.5


                # Map directly outwards from the true center pixels of your monitor layout
                target_x = (screen_w / 2) + (offset_x * GAIN_X * screen_w)
                target_y = (screen_h / 2) + (offset_y * GAIN_Y * screen_h)


                # 4. Smoothing Filter Engine
                curr_x = (target_x * SMOOTH_FACTOR) + (prev_x * (1 - SMOOTH_FACTOR))
                curr_y = (target_y * SMOOTH_FACTOR) + (prev_y * (1 - SMOOTH_FACTOR))


                # 5. Screen Boundary Safety Clip
                final_x = int(np.clip(curr_x, 0, screen_w - 1))
                final_y = int(np.clip(curr_y, 0, screen_h - 1))
               
                # Execute Cursor Position Update
                if time_since_manual > RESUME_DELAY:
                    if abs(final_x - prev_x) > DEADZONE or abs(final_y - prev_y) > DEADZONE:
                        pyautogui.moveTo(final_x, final_y, _pause=False)
                        prev_x, prev_y = final_x, final_y


            # Draw visual tracking contours onto dashboard frame array
            eye_pts = np.array([[int(landmarks[idx].x * img_w), int(landmarks[idx].y * img_h)] for idx in RIGHT_EYE_CONTOUR])
            draw_color = (0, 0, 255) if time_since_manual < RESUME_DELAY else (0, 255, 0)
            cv2.polylines(frame, [eye_pts], True, draw_color, 1)


            px_x, px_y = int(iris.x * img_w), int(iris.y * img_h)
            cv2.circle(frame, (px_x, px_y), 4, (0, 255, 255), -1)


        # =================================================================
        # UI PIPELINE CALLBACK
        # =================================================================
        if not app_callback(frame):
            break


    cam.release()
    print(">>> [Eye Thread] Eyeball Tracking hardware pipeline dropped safely.")