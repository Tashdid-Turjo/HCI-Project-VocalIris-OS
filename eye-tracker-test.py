import cv2
import mediapipe as mp
import pyautogui

# 1. Setup MediaPipe Face Mesh (for Iris tracking)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True) 

# 2. Setup Camera
cam = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

print("System started. Look at the camera to move the mouse. Press 'q' to quit.")

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1) # Flip like a mirror
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 3. Process the frame for landmarks
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    
    if landmark_points:
        landmarks = landmark_points[0].landmark
        
        # 4. Use specific landmark for the Eye (474 is a standard iris point)
        eye = landmarks[474] 
        
        # 5. Map Landmark (0.0 to 1.0) to Screen Pixels
        # This acts as your 'Mouse Pointer'
        mouse_x = int(eye.x * screen_w)
        mouse_y = int(eye.y * screen_h)
        
        # 6. Move the actual Windows cursor
        pyautogui.moveTo(mouse_x, mouse_y)

    # Show the webcam feed (The UI/UX part)
    cv2.imshow('VocalIris Eye Tracker Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()