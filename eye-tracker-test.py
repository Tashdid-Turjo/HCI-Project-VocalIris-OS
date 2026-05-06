import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Setup the Task Base
model_path = 'face_landmarker.task' 

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# 2. Setup Camera (Index 1 was your working port)
cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
screen_w, screen_h = pyautogui.size()

if not cam.isOpened():
    print("Error: Could not open camera at Index 1.")
else:
    print("VocalIris OS: Active. Look at the screen to move the mouse. Press 'q' to quit.")

while cam.isOpened():
    success, frame = cam.read()
    if not success:
        continue # Use continue so it keeps trying if a frame is dropped

    # Flip for mirror effect and convert color
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # MediaPipe detection
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    # 3. Process Landmarks & Move Mouse
    if detection_result and detection_result.face_landmarks:
        landmarks = detection_result.face_landmarks[0]
        
        # Landmark 474: Right Iris Center
        iris_point = landmarks[474]
        
        # Map to Screen
        mouse_x = int(iris_point.x * screen_w)
        mouse_y = int(iris_point.y * screen_h)
        
        # Move Cursor instantly
        pyautogui.moveTo(mouse_x, mouse_y, _pause=False)

    # 4. Show the Window
    cv2.imshow('VocalIris OS - Eye Tracker', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()