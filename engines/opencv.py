import cv2

def check_cameras(max_to_test=5):
    available_indices = []
    for i in range(max_to_test):
        # CAP_DSHOW is often faster on Windows for checking ports
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Index {i}: WORKING (Camera detected)")
                available_indices.append(i)
            else:
                print(f"Index {i}: OPEN but not reading (Check if another app is using it)")
            cap.release()
        else:
            print(f"Index {i}: NOT FOUND")
    return available_indices

print("Scanning for cameras...")
working_ports = check_cameras()
print(f"\nFinal list of working indices: {working_ports}")