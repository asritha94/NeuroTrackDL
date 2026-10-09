import csv
import time
import os
import cv2
import numpy as np
import mediapipe as mp
import math
log_file = "fatigue_log.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "blink_count",
            "eye_state",
            "pitch",
            "yaw",
            "roll",
            "fatigue"
        ])

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils

# 3D model points (approximate)
model_points = np.array([
    (0.0, 0.0, 0.0),          # Nose tip
    (0.0, -330.0, -65.0),     # Chin
    (-225.0, 170.0, -135.0),  # Left eye corner
    (225.0, 170.0, -135.0),   # Right eye corner
    (-150.0, -150.0, -125.0),# Left mouth corner
    (150.0, -150.0, -125.0)  # Right mouth corner
])

cap = cv2.VideoCapture(0)
log_file = "fatigue_log.csv"

if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "pitch",
            "yaw",
            "roll",
            "fatigue"
        ])

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            landmarks = face_landmarks.landmark  # ✅ IMPORTANT FIX

            # Draw landmarks
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1)
            )

            # 2D image points
            image_points = np.array([
                (landmarks[1].x * w, landmarks[1].y * h),     # Nose tip
                (landmarks[152].x * w, landmarks[152].y * h), # Chin
                (landmarks[33].x * w, landmarks[33].y * h),   # Left eye
                (landmarks[263].x * w, landmarks[263].y * h), # Right eye
                (landmarks[61].x * w, landmarks[61].y * h),   # Left mouth
                (landmarks[291].x * w, landmarks[291].y * h)  # Right mouth
            ], dtype="double")

            # Camera matrix
            focal_length = w
            cam_matrix = np.array([
                [focal_length, 0, w / 2],
                [0, focal_length, h / 2],
                [0, 0, 1]
            ])

            dist_coeffs = np.zeros((4, 1))

            success, rot_vec, trans_vec = cv2.solvePnP(
                model_points,
                image_points,
                cam_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            if success:
                # Project nose direction
                nose_3d = np.array([(0, 0, 1000.0)])
                nose_2d, _ = cv2.projectPoints(
                    nose_3d, rot_vec, trans_vec, cam_matrix, dist_coeffs
                )

                p1 = (int(image_points[0][0]), int(image_points[0][1]))
                p2 = (int(nose_2d[0][0][0]), int(nose_2d[0][0][1]))

                cv2.line(frame, p1, p2, (255, 0, 0), 3)

                # Convert rotation to angles
                rmat, _ = cv2.Rodrigues(rot_vec)
                angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

                pitch = angles[0] * 360
                yaw = angles[1] * 360
                roll = angles[2] * 360
                current_time = time.strftime("%H:%M:%S")

                # Simple fatigue logic (for now)
                if abs(pitch) > 15 or abs(yaw) > 15:
                    fatigue = "High"
                else:
                    fatigue = "Normal"

                with open(log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        current_time,
                        round(pitch, 2),
                        round(yaw, 2),
                        round(roll, 2),
                        fatigue
                    ])

                cv2.putText(frame, f"Pitch: {pitch:.2f}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Yaw: {yaw:.2f}", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Roll: {roll:.2f}", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Head Pose + Face Landmarks", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
