import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Setup the Task Base
# NOTE: You need the 'face_landmarker.task' file in your folder!
model_path = 'face_landmarker.task' 

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# 2. Setup Camera
cam = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

while cam.isOpened():
    success, frame = cam.read()
    if not success: break               ## If add continue, it doesn't detect, kinda crashes.

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # MediaPipe modern API requires an 'Image' object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # 3. Detect Landmarks
    detection_result = detector.detect(mp_image)

    # 4. Extract Iris/Eye data
    if detection_result and detection_result.face_landmarks:
        # Landmarks are now in a nested list
        landmarks = detection_result.face_landmarks[0]
        
        # Landmark index 474 is still the center of the right iris
        iris_point = landmarks[474]
        
        # 5. Coordinate Mapping
        mouse_x = int(iris_point.x * screen_w)
        mouse_y = int(iris_point.y * screen_h)
        
        # 6. Move Cursor (Smoothly move to prevent jitter)
        pyautogui.moveTo(mouse_x, mouse_y, _pause=False)


    ##### Directly shows error message. Doesn't take time. #####
    # else:
    # # If no face is seen, just print a warning instead of crashing
    # print("No face detected... looking...")

    cv2.imshow('VocalIris OS - Modern Engine', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()