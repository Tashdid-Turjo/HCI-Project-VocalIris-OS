import cv2
import mediapipe as mp
import pyautogui
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def run_face_detection(app_callback):
    """
    Wraps your backup face detection engine.
    Feeds frames back to the UI canvas instead of opening cv2.imshow.
    """
    # 1. Setup the Task Base
    model_path = 'face_landmarker.task' 

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)

    # 2. Setup Camera (Using Index 1 as per your hardware setup)
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    screen_w, screen_h = pyautogui.size()

    # Variables for manual movement detection
    last_mouse_x, last_mouse_y = pyautogui.position()
    last_manual_move_time = 0

    if not cam.isOpened():
        print("Error: Could not open camera at Index 1.")
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