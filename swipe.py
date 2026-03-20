import cv2
import time
import pyautogui
import mediapipe as mp

"""
Requirements:
pip install opencv-python mediapipe pyautogui

Controls:
- Open mouth (slightly)  -> ACTIVATED
- Close mouth           -> DEACTIVATED
- Turn head RIGHT -> next desktop
- Turn head LEFT  -> previous desktop
"""

# Init
cap = cv2.VideoCapture(0)
mp_face = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

face_mesh = mp_face.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Mouth landmarks
UPPER_LIP = 13
LOWER_LIP = 14

# Variables
activated = False
cooldown = 1
last_action = 0
ref_nose_x = None

while True:
    success, frame = cap.read()
    if not success:
        break

    # Mirror frame for natural control
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:

            landmarks = face_landmarks.landmark

            # Mouth detection (sensitive)
            upper = landmarks[UPPER_LIP]
            lower = landmarks[LOWER_LIP]

            mouth_open = abs(upper.y - lower.y) > 0.015

            # Activation state
            if mouth_open:
                activated = True
            else:
                activated = False
                ref_nose_x = None

            # Nose position
            nose = landmarks[1]
            nose_x = nose.x

            current_time = time.time()

            # Movement detection
            if activated:
                if ref_nose_x is None:
                    ref_nose_x = nose_x

                dx = nose_x - ref_nose_x

                if current_time - last_action > cooldown:
                    # RIGHT -> next desktop
                    if dx < -0.07:
                        pyautogui.hotkey('ctrl', 'win', 'right')
                        last_action = current_time
                        ref_nose_x = None

                    # LEFT -> previous desktop
                    elif dx > 0.07:
                        pyautogui.hotkey('ctrl', 'win', 'left')
                        last_action = current_time
                        ref_nose_x = None

# Clean exit
cap.release()
cv2.destroyAllWindows()
