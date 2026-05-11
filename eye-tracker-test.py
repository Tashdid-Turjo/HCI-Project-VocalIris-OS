import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- VOSK VOICE SETUP ---
VOSK_MODEL_PATH = "model" # Path to your unzipped vosk model folder
voice_queue = queue.Queue()

def voice_callback(indata, frames, time, status):
    """This captures audio chunks from the mic"""
    voice_queue.put(bytes(indata))

def voice_recognition_thread():
    model = Model(VOSK_MODEL_PATH)
    # We restrict the dictionary to ONLY these words to make it 100% accurate
    rec = KaldiRecognizer(model, 16000, '["click", "select", "double", "right", "close"]')
    
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=voice_callback):
        print("Vosk Voice Engine: Active.")
        while True:
            data = voice_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                command = result.get("text", "")
                
                if "click" in command or "select" in command:
                    print("COMMAND: Left Click")
                    pyautogui.click()
                elif "double" in command:
                    print("COMMAND: Double Click")
                    pyautogui.doubleClick()
                elif "right" in command:
                    print("COMMAND: Right Click")
                    pyautogui.rightClick()

# Start the voice thread immediately (ensures the microphone is always listening in the background without making the camera lag)
threading.Thread(target=voice_recognition_thread, daemon=True).start()

# --- EYE TRACKER SETUP (MediaPipe Tasks) ---
pyautogui.FAILSAFE = False
model_path = 'face_landmarker.task' 

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# --- CONFIGURATION ---
SENSITIVITY_X = 5.5  
SENSITIVITY_Y = 4.5  
SMOOTH_FACTOR = 0.12 
DEADZONE = 2         
OVERRIDE_THRESHOLD = 10 # Pixels moved manually to trigger override
RESUME_DELAY = 2.0      # Seconds to wait after manual movement

# Right Eye Landmark Indices
RIGHT_EYE_CONTOUR = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

# Tracking state
prev_x, prev_y = pyautogui.position()
last_manual_move_time = 0

# 2. Setup Camera
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
screen_w, screen_h = pyautogui.size()

print("VocalIris OS: Active. Move your physical mouse to override eye tracking.")

while cam.isOpened():
    success, frame = cam.read()
    if not success: continue

    frame = cv2.flip(frame, 1)
    img_h, img_w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    # --- 3. MANUAL OVERRIDE CHECK ---
    # Check current real mouse position
    actual_x, actual_y = pyautogui.position()
    
    # If the mouse is NOT where our code last put it, the user moved it manually
    if abs(actual_x - prev_x) > OVERRIDE_THRESHOLD or abs(actual_y - prev_y) > OVERRIDE_THRESHOLD:
        last_manual_move_time = time.time()
        # Synchronize our tracking state to the manual position
        prev_x, prev_y = actual_x, actual_y

    # Calculate time since last manual touch
    time_since_manual = time.time() - last_manual_move_time

    if detection_result and detection_result.face_landmarks:
        landmarks = detection_result.face_landmarks[0]
        
        # Landmarks
        iris = landmarks[474]
        l_corner, r_corner = landmarks[33], landmarks[133]
        t_edge, b_edge = landmarks[159], landmarks[145]

        # 1. Coordinate Mapping
        rel_x = (iris.x - l_corner.x) / (r_corner.x - l_corner.x)
        rel_y = (iris.y - t_edge.y) / (b_edge.y - t_edge.y)

        # 2. Target Calculation
        target_x = ((rel_x - 0.5) * SENSITIVITY_X * screen_w) + (screen_w / 2)
        target_y = ((rel_y - 0.5) * SENSITIVITY_Y * screen_h) + (screen_h / 2)

        # 3. Apply Smoothing
        curr_x = (target_x * SMOOTH_FACTOR) + (prev_x * (1 - SMOOTH_FACTOR))
        curr_y = (target_y * SMOOTH_FACTOR) + (prev_y * (1 - SMOOTH_FACTOR))

        final_x = int(np.clip(curr_x, 0, screen_w - 1))
        final_y = int(np.clip(curr_y, 0, screen_h - 1))
        
        # --- 4. EXECUTE MOVEMENT ONLY IF NOT OVERRIDDEN ---
        if time_since_manual > RESUME_DELAY:
            if abs(final_x - prev_x) > DEADZONE or abs(final_y - prev_y) > DEADZONE:
                pyautogui.moveTo(final_x, final_y, _pause=False)
                prev_x, prev_y = final_x, final_y
        
        # --- DRAWING ---
        eye_pts = np.array([[int(landmarks[idx].x * img_w), int(landmarks[idx].y * img_h)] for idx in RIGHT_EYE_CONTOUR])
        # Change outline color to RED if overridden, GREEN if active
        draw_color = (0, 0, 255) if time_since_manual < RESUME_DELAY else (0, 255, 0)
        cv2.polylines(frame, [eye_pts], True, draw_color, 1)

        px_x, px_y = int(iris.x * img_w), int(iris.y * img_h)
        cv2.circle(frame, (px_x, px_y), 4, (0, 255, 255), -1)

    cv2.imshow('VocalIris OS - Eye Tracker (Override Ready)', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cam.release()
cv2.destroyAllWindows()