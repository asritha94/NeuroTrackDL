# 🧠 NeuroTrackDL – Real-Time Driver Fatigue Monitoring System

NeuroTrackDL is a Python-based computer vision application designed to monitor signs of fatigue through real-time facial analysis using a webcam. It analyzes eye movements, blink patterns, Eye Aspect Ratio (EAR), and head pose to estimate fatigue levels and provide recommendations to help users take appropriate breaks.

The application provides a web-based dashboard built with Flask, user registration and login, live webcam monitoring, fatigue status visualization, and session-based analysis.

## 📌 Project Overview

* **Project Name:** NeuroTrackDL
* **Project Type:** Computer Vision and Fatigue Monitoring System
* **Frontend:** HTML5, CSS3, JavaScript
* **Backend:** Python, Flask
* **Computer Vision:** OpenCV, MediaPipe
* **Numerical Processing:** NumPy
* **Database:** SQLite
* **Data Logging:** CSV and JSON

## ✨ Key Features

### 1. User Authentication

* User registration and login.
* Password hashing for storing credentials.
* Forgot-password and change-password functionality.
* SQLite database for user account information.

### 2. Real-Time Webcam Monitoring

* Captures live video through the computer's webcam.
* Detects facial landmarks using MediaPipe Face Mesh.
* Processes facial movements during an analysis session.
* Displays live monitoring information on the dashboard.

### 3. Eye Blink Detection

* Tracks eye landmarks to identify eye-opening and eye-closing patterns.
* Calculates the Eye Aspect Ratio (EAR).
* Detects blinks based on eye closure across consecutive frames.
* Maintains a running blink count.

### 4. Head Pose Estimation

* Estimates head orientation using facial landmarks and OpenCV.
* Calculates head pose angles: pitch, yaw, and roll.
* Uses head movement as an additional indicator for fatigue analysis.

### 5. Fatigue Level Estimation

* Analyzes blink count, EAR, and head pose.
* Evaluates monitoring data to estimate fatigue levels.
* Provides recommendations based on the calculated fatigue status.

### 6. Live Dashboard and Graphs

* Displays webcam monitoring and facial analysis information.
* Shows blink count, EAR, head pose, and fatigue status.
* Provides visual representations of monitoring data where implemented.
* Displays the final analysis results.

### 7. Timed Analysis and Retake

* Runs fatigue analysis for a defined monitoring period.
* Stops live analysis when the configured timer reaches zero.
* Preserves the completed session's results for review.
* Allows the user to start another analysis using the retake or recheck option, where implemented.

### 8. Data Logging and Recommendations

* Stores monitoring information in CSV files.
* Uses JSON to maintain the latest analysis status.
* Generates fatigue-related recommendations.
* Includes a fatigue graph utility for visualizing logged measurements.

## ⚙️ How the Project Works

The application follows this workflow:

1. **Register or log in:** The user creates an account or signs in through the Flask web interface.
2. **Open the dashboard:** After login, the user accesses the fatigue monitoring dashboard.
3. **Start monitoring:** The application accesses the webcam and begins capturing live video.
4. **Detect facial landmarks:** MediaPipe identifies facial landmarks, including the points around the eyes.
5. **Calculate EAR:** The system calculates the Eye Aspect Ratio to estimate whether the eyes are open or closed.
6. **Count blinks:** Consecutive frames with eye closure are analyzed to identify blinks.
7. **Estimate head pose:** OpenCV processes facial landmark coordinates to estimate pitch, yaw, and roll.
8. **Evaluate fatigue:** The system uses blink count, EAR, and head pose thresholds to estimate the fatigue level.
9. **Display results:** The dashboard displays the monitoring measurements, fatigue status, and relevant recommendations.
10. **Save monitoring data:** The latest status is maintained in JSON, while supported measurements and results are logged in CSV.
11. **Complete or repeat analysis:** When the analysis timer finishes, the webcam monitoring stops and the completed results can remain visible. The user can start another session using the retake option if enabled in the current dashboard.

## 🧮 Fatigue Evaluation Logic

The project uses threshold-based rules to estimate fatigue. The smart scheduling module evaluates blink count, EAR, and head pitch.

| Condition                                                                       | Estimated level | Recommendation                                      |
| ------------------------------------------------------------------------------- | --------------- | --------------------------------------------------- |
| Blink count greater than 20, EAR below 0.20, or absolute pitch greater than 20° | High            | Take a 5–10 minute break, stretch, and drink water  |
| Blink count greater than 10, EAR below 0.23, or absolute pitch greater than 15° | Medium          | Switch to lighter tasks or reduce screen brightness |
| None of the above conditions                                                    | Low             | Continue working                                    |

These rules are implemented in `smart_scheduler.py`. The live analysis module also contains its own fatigue evaluation logic, so the precise status displayed depends on which evaluation path is active.

**Note:** These are heuristic estimates, not a medical diagnosis or a validated measurement of driver fitness.

## 🛠️ Technologies Used

| Technology | Purpose                             |
| ---------- | ----------------------------------- |
| Python     | Core application logic              |
| Flask      | Web server and application routes   |
| HTML5      | Web page structure                  |
| CSS3       | Dashboard styling                   |
| JavaScript | Browser-side interactions           |
| OpenCV     | Webcam capture and image processing |
| MediaPipe  | Facial landmark detection           |
| NumPy      | Numerical calculations              |
| SQLite     | User account database               |
| CSV        | Fatigue and monitoring logs         |
| JSON       | Current monitoring status           |
| Matplotlib | Fatigue graph visualization         |
| Pandas     | Processing logged monitoring data   |

## 📂 Project Structure

```text
NeuroTrackDL/
├── app.py
├── camera.py
├── blink_detection.py
├── head_pose.py
├── smart_scheduler.py
├── neurotrack_main.py
├── fatigue_graph.py
├── init_db.py
├── test_mediapipe.py
├── current_status.json
├── fatigue_log.csv
├── users.db
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── forgot_password.html
│   └── change_password.html
├── README.md
└── .gitignore
```

### Important Files

* **`app.py`** – Flask application, authentication routes, and dashboard endpoints.
* **`camera.py`** – Webcam capture, real-time facial analysis, blink tracking, head pose, and monitoring session management.
* **`blink_detection.py`** – Standalone eye blink detection and EAR calculation.
* **`head_pose.py`** – Standalone head pose estimation using facial landmarks.
* **`smart_scheduler.py`** – Threshold-based fatigue evaluation and recommendations.
* **`neurotrack_main.py`** – Reads current monitoring status, applies smart scheduling rules, and logs results.
* **`fatigue_graph.py`** – Generates a graph from the monitoring CSV file.
* **`init_db.py`** – Creates the SQLite users table.
* **`current_status.json`** – Stores the latest monitoring measurements and fatigue status.
* **`fatigue_log.csv`** – Stores logged fatigue measurements.
* **`templates/`** – Contains the HTML pages for authentication and the dashboard.

## 🚀 Installation and Setup

### Prerequisites

Install the following:

* Python 3.10 or another compatible Python version.
* pip package manager.
* Visual Studio Code or another code editor.
* A working webcam.
* Git (optional, for cloning the repository).

### Step 1: Clone the Repository

```bash
git clone https://github.com/asritha94/NeuroTrackDL.git
cd NeuroTrackDL
```

If you already have the project, open its root folder in VS Code.

### Step 2: Create a Virtual Environment

On Windows:

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

For Command Prompt:

```bash
venv\Scripts\activate
```

For PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

Install the required packages:

```bash
pip install flask opencv-python mediapipe numpy pandas matplotlib
```

If your project has a `requirements.txt` file, use that file instead:

```bash
pip install -r requirements.txt
```

### Step 5: Initialize the Database

```bash
python init_db.py
```

This creates the SQLite database and the users table if they do not already exist.

### Step 6: Run the Application

```bash
python app.py
```

### Step 7: Open the Application

Open the local URL displayed in the terminal. The typical Flask development URL is:

```text
http://127.0.0.1:5000/
```

Register an account, log in, and navigate to the dashboard to test the monitoring workflow.


## 🔒 Privacy and Safety

* Webcam access requires user permission and a working camera.
* Avoid committing real user records, database files containing personal information, or sensitive monitoring logs to a public repository.
* Use environment variables and secure configuration for deployment.
* This project is intended as a monitoring and educational prototype. Its fatigue estimates should not be used as the sole basis for driving or other safety-critical decisions.

## 🔮 Future Enhancements

* Improve fatigue estimation using a validated machine learning model.
* Add historical session reports and trend analysis.
* Improve monitoring reliability under different lighting conditions.
* Add stronger session management and account security.
* Introduce configurable alerts and break reminders.
* Deploy the application using a production-ready server.

## 🎯 Project Objective

The objective of NeuroTrackDL is to develop a real-time fatigue monitoring application that combines computer vision, facial landmark detection, eye blink analysis, head pose estimation, and web-based visualization to identify potential signs of fatigue and provide timely recommendations.

## 👩‍💻 Author

I. Asritha 



