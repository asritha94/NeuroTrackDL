import csv
import os
import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Eye landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Eye Aspect Ratio (EAR) calculation
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

# Webcam
cap = cv2.VideoCapture(0)
log_file = "fatigue_log.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "blink_count",
            "eye_state",
            "ear"
        ])

blink_count = 0
ear_threshold = 0.25
frame_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0].landmark

        left_eye = np.array([
            (int(face_landmarks[i].x * w), int(face_landmarks[i].y * h))
            for i in LEFT_EYE
        ])
        right_eye = np.array([
            (int(face_landmarks[i].x * w), int(face_landmarks[i].y * h))
            for i in RIGHT_EYE
        ])

        # Draw eye landmarks
        for (x, y) in np.concatenate((left_eye, right_eye)):
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
        current_time = time.strftime("%H:%M:%S")

        eye_state = "Closed" if ear < ear_threshold else "Open"

        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                current_time,
                blink_count,
                eye_state,
                round(ear, 2)
            ])

        if ear < ear_threshold:
            frame_counter += 1
        else:
            if frame_counter >= 2:
                blink_count += 1
            frame_counter = 0

        # Display info
        cv2.putText(frame, f"Blinks: {blink_count}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"EAR: {ear:.2f}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.imshow("Eye Blink Detection - NeuroTrackDL", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
