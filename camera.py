import cv2
import mediapipe as mp
import numpy as np
import json
import time
import threading

# ================= MediaPipe Setup =================
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ================= Eye Landmarks =================
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# ================= Blink Settings =================
EAR_THRESHOLD = 0.23
BLINK_FRAMES = 3

blink_count = 0
frame_counter = 0
minute_start_time = 0
minute_ear_values = []
final_fatigue = "ANALYZING"
final_suggestion = "Collecting data..."

# ================= Head Pose Model =================
model_points = np.array([
    (0.0, 0.0, 0.0),
    (0.0, -330.0, -65.0),
    (-225.0, 170.0, -135.0),
    (225.0, 170.0, -135.0),
    (-150.0, -150.0, -125.0),
    (150.0, -150.0, -125.0)
])

state_lock = threading.RLock()
cap = None
analysis_active = False
analysis_session = 0
active_streams = set()
latest_status = {
    "time": "--",
    "ear": 0,
    "blink_count": 0,
    "pitch": 0,
    "yaw": 0,
    "roll": 0,
    "fatigue": final_fatigue,
    "suggestion": final_suggestion
}


def _write_status_locked():
    with open("current_status.json", "w") as status_file:
        json.dump(latest_status, status_file)


def _release_camera_locked():
    global cap

    if cap is not None:
        cap.release()
        cap = None


def _finish_analysis_locked():
    global analysis_active, final_fatigue, final_suggestion

    if analysis_active:
        avg_ear = sum(minute_ear_values) / len(minute_ear_values) if minute_ear_values else 0

        if avg_ear < 0.24 or blink_count > 25:
            final_fatigue = "HIGH"
            final_suggestion = "Take a 5–10 min break"
        else:
            final_fatigue = "NORMAL"
            final_suggestion = "Good focus, continue"

        analysis_active = False

    latest_status.update({
        "time": time.strftime("%H:%M:%S"),
        "blink_count": blink_count,
        "fatigue": final_fatigue,
        "suggestion": final_suggestion
    })
    _write_status_locked()


def start_analysis():
    global cap, analysis_active, analysis_session
    global blink_count, frame_counter, minute_start_time, minute_ear_values
    global final_fatigue, final_suggestion, latest_status

    with state_lock:
        if analysis_active:
            return analysis_session

        new_cap = cv2.VideoCapture(0)
        if not new_cap.isOpened():
            new_cap.release()
            return None

        _release_camera_locked()
        cap = new_cap
        analysis_session += 1
        analysis_active = True
        blink_count = 0
        frame_counter = 0
        minute_start_time = 0
        minute_ear_values = []
        final_fatigue = "ANALYZING"
        final_suggestion = "Collecting data..."
        latest_status = {
            "time": time.strftime("%H:%M:%S"),
            "ear": 0,
            "blink_count": 0,
            "pitch": 0,
            "yaw": 0,
            "roll": 0,
            "fatigue": final_fatigue,
            "suggestion": final_suggestion
        }
        _write_status_locked()
        return analysis_session


def get_active_session():
    with state_lock:
        return analysis_session if analysis_active else None


def stop_analysis():
    with state_lock:
        _finish_analysis_locked()
        _release_camera_locked()
        return latest_status.copy()

# ================= EAR Function =================
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

# ================= Video Stream =================
def generate_frames(session_id):
    global analysis_active
    global blink_count, frame_counter
    global minute_start_time, minute_ear_values
    with state_lock:
        if not analysis_active or session_id != analysis_session or session_id in active_streams:
            return
        minute_start_time = time.monotonic()
        active_streams.add(session_id)

    try:
        while True:
            with state_lock:
                if not analysis_active or session_id != analysis_session or cap is None:
                    break

                success, frame = cap.read()
                if not success:
                    _finish_analysis_locked()
                    _release_camera_locked()
                    break

                h, w, _ = frame.shape
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb)

                ear = 0
                pitch = yaw = roll = 0
                pose_valid = False

                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark

                    # ---------- GREEN FACE MESH ----------
                    mp_drawing.draw_landmarks(
                        frame,
                        results.multi_face_landmarks[0],
                        mp_face_mesh.FACEMESH_CONTOURS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1),
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                    )

                    # ---------- Blink Detection ----------
                    left_eye = np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in LEFT_EYE])
                    right_eye = np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in RIGHT_EYE])

                    ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2
                    minute_ear_values.append(ear)

                    if ear < EAR_THRESHOLD:
                        frame_counter += 1
                    else:
                        if frame_counter >= BLINK_FRAMES:
                            blink_count += 1
                        frame_counter = 0

                    for (x, y) in np.concatenate((left_eye, right_eye)):
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                    # ---------- Head Pose ----------
                    image_points = np.array([
                        (landmarks[1].x * w, landmarks[1].y * h),
                        (landmarks[152].x * w, landmarks[152].y * h),
                        (landmarks[33].x * w, landmarks[33].y * h),
                        (landmarks[263].x * w, landmarks[263].y * h),
                        (landmarks[61].x * w, landmarks[61].y * h),
                        (landmarks[291].x * w, landmarks[291].y * h)
                    ], dtype="double")

                    cam_matrix = np.array([
                        [w, 0, w / 2],
                        [0, w, h / 2],
                        [0, 0, 1]
                    ])
                    dist_coeffs = np.zeros((4, 1))

                    success, rot_vec, _ = cv2.solvePnP(
                        model_points, image_points, cam_matrix, dist_coeffs
                    )

                    if success:
                        rmat, _ = cv2.Rodrigues(rot_vec)
                        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
                        pitch, yaw, roll = [a * 360 for a in angles]
                        pose_valid = True

                latest_status.update({
                    "time": time.strftime("%H:%M:%S"),
                    "ear": round(ear, 3),
                    "blink_count": blink_count,
                    "fatigue": "ANALYZING",
                    "suggestion": "Collecting data..."
                })
                if pose_valid:
                    latest_status.update({
                        "pitch": round(pitch, 2),
                        "yaw": round(yaw, 2),
                        "roll": round(roll, 2)
                    })

                finished = time.monotonic() - minute_start_time >= 60
                if finished:
                    _finish_analysis_locked()

                _write_status_locked()

                ret, buffer = cv2.imencode(".jpg", frame)
                if not ret:
                    _finish_analysis_locked()
                    _release_camera_locked()
                    break
                encoded_frame = buffer.tobytes()

                if finished:
                    _release_camera_locked()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + encoded_frame + b"\r\n")

            if finished:
                break
    finally:
        with state_lock:
            active_streams.discard(session_id)
            if analysis_active and session_id == analysis_session:
                if time.monotonic() - minute_start_time >= 60:
                    _finish_analysis_locked()
                _release_camera_locked()
                analysis_active = False
