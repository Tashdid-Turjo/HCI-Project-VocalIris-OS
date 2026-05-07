### Need more implementation:

import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Setup the Task Base
pyautogui.FAILSAFE = False
model_path = 'face_landmarker.task' 



base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# 2. Setup Camera
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
screen_w, screen_h = pyautogui.size()

# Sensitivity setting: higher = mouse moves further with less eye effort
SENSITIVITY = 2.0 

if not cam.isOpened():
    print("Error: Could not open camera at Index 1.")
else:
    print("VocalIris OS: EYE-ONLY mode active. Press 'q' to quit.")

while cam.isOpened():
    success, frame = cam.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    # 3. Process Relative Eye Movement
    if detection_result and detection_result.face_landmarks:
        landmarks = detection_result.face_landmarks[0]
        
        # Landmarks for Right Eye
        iris = landmarks[474]       # The moving pupil
        left_corner = landmarks[33]  # Fixed anchor 1
        right_corner = landmarks[133] # Fixed anchor 2
        
        # Vertical anchors for Y-axis
        top_edge = landmarks[159]
        bottom_edge = landmarks[145]

        # CALCULATE RATIO (Horizontal)
        # Finds where iris is between corners (0.0 to 1.0)
        column_width = right_corner.x - left_corner.x
        relative_x = (iris.x - left_corner.x) / column_width
        
        # CALCULATE RATIO (Vertical)
        row_height = bottom_edge.y - top_edge.y
        relative_y = (iris.y - top_edge.y) / row_height

        # MAP TO SCREEN
        # We subtract 0.5 to center the movement at the middle of the screen
        mouse_x = int(screen_w * (relative_x - 0.5) * SENSITIVITY + (screen_w / 2))
        mouse_y = int(screen_h * (relative_y - 0.5) * SENSITIVITY + (screen_h / 2))
        
        # MOVE MOUSE
        # Constrain coordinates to stay on screen
        mouse_x = max(0, min(screen_w, mouse_x))
        mouse_y = max(0, min(screen_h, mouse_y))
        
        pyautogui.moveTo(mouse_x, mouse_y, _pause=False)

        # Optional: Draw markers for debugging
        cv2.circle(frame, (int(iris.x * frame.shape[1]), int(iris.y * frame.shape[0])), 2, (0, 255, 0), -1)

    cv2.imshow('VocalIris OS - True Eye Tracker', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()