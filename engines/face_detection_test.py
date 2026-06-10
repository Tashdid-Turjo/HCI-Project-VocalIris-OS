import cv2
import mediapipe as mp
import pyautogui
import time
import os
import sys
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def run_face_detection(app_callback):
    """
    Wraps your backup face detection engine.
    Feeds frames back to the UI canvas instead of opening cv2.imshow.
    """
    # 1. Setup the Task Base (Patched dynamically for standalone .exe execution)
    if getattr(sys, 'frozen', False):
        # Running inside the compiled PyInstaller .exe context
        base_path = sys._MEIPASS
    else:
        # Running as a loose script in Git Bash
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    model_path = os.path.join(base_path, 'face_landmarker.task') 

    # CRITICAL FIX: Read the model file directly into memory as a binary buffer
    # This prevents MediaPipe from crashing inside the compiled executable wrapper!
    try:
        with open(model_path, 'rb') as f:
            model_buffer = f.read()
    except Exception as e:
        print(f"Error loading model file at {model_path}: {e}")
        return

    # Pass the raw memory buffer instead of a file path string
    base_options = python.BaseOptions(model_asset_buffer=model_buffer)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)

    # 2. Setup Camera (Dynamic Fallback Scan Loop for USB/OBS Virtual Cams)
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

    # Safety emergency fallback if everything fails to scan
    if cam is None:
        print(">>> [CRITICAL] No active hardware or virtual cameras detected on indexes 0-3. Attempting default...")
        cam = cv2.VideoCapture(0)

    screen_w, screen_h = pyautogui.size()

    # Variables for manual movement detection
    last_mouse_x, last_mouse_y = pyautogui.position()
    last_manual_move_time = 0

    if not cam.isOpened():
        print("Error: Could not open camera framework entirely.")
        return

    print("VocalIris OS Engine: Face Tracking Loop Engaged.")

    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            continue

        # Flip for mirror effect and convert color
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe detection
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        # Check for manual movement
        current_mouse_x, current_mouse_y = pyautogui.position()
        if abs(current_mouse_x - last_mouse_x) > 5 or abs(current_mouse_y - last_mouse_y) > 5:
            last_manual_move_time = time.time()

        # 3. Process Landmarks & Move Mouse
        if detection_result and detection_result.face_landmarks:
            if time.time() - last_manual_move_time > 1.0:
                landmarks = detection_result.face_landmarks[0]
                iris_point = landmarks[474]
                
                # Map to Screen
                mouse_x = int(iris_point.x * screen_w)
                mouse_y = int(iris_point.y * screen_h)
                
                # Move Cursor instantly
                pyautogui.moveTo(mouse_x, mouse_y, _pause=False)
                last_mouse_x, last_mouse_y = mouse_x, mouse_y
            else:
                last_mouse_x, last_mouse_y = current_mouse_x, current_mouse_y

        # =================================================================
        # UI PIPELINE CALLBACK
        # Pass the processed frame matrix upstream to our dashboard layout.
        # If it returns False, it means the user clicked 'OFF'. Stop immediately!
        # =================================================================
        if not app_callback(frame):
            break

    # Clean up hardware connections completely
    cam.release()
    print(">>> [Eye Thread] Face Tracking hardware pipeline dropped safely.")