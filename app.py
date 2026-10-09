from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import json
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from camera import (
    generate_frames,
    get_active_session,
    start_analysis,
    stop_analysis
)

app = Flask(__name__)

# ================= DATABASE CONNECTION =================
def get_db():
    return sqlite3.connect("users.db")


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        con.close()

        if user and check_password_hash(user[0], password):
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password"

    return render_template("login.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            con = get_db()
            cur = con.cursor()
            cur.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            con.commit()
            con.close()
            return redirect(url_for("login"))
        except:
            return "Username already exists"

    return render_template("register.html")


# ================= FORGOT PASSWORD =================
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        new_password = generate_password_hash(request.form["password"])

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if user:
            cur.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_password, username)
            )
            con.commit()
            con.close()
            return redirect(url_for("login"))
        else:
            con.close()
            return "User not found"

    return render_template("forgot_password.html")


# ================= CHANGE PASSWORD =================
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        username = request.form["username"]
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user[0], old_password):
            cur.execute(
                "UPDATE users SET password=? WHERE username=?",
                (generate_password_hash(new_password), username)
            )
            con.commit()
            con.close()
            return "Password changed successfully"
        else:
            con.close()
            return "Invalid credentials"

    return render_template("change_password.html")


# ================= DASHBOARD (UNCHANGED) =================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ================= ANALYSIS SESSION =================
@app.route("/start_analysis", methods=["POST"])
def start_analysis_route():
    session_id = start_analysis()
    if session_id is None:
        return jsonify({
            "error": "Unable to access the webcam. Check that a camera is connected and available."
        }), 503
    return jsonify({"session_id": session_id})


@app.route("/stop_analysis", methods=["POST"])
def stop_analysis_route():
    return jsonify(stop_analysis())


# ================= LIVE WEBCAM STREAM =================
@app.route("/video_feed")
def video_feed():
    session_id = get_active_session()
    if session_id is None:
        return jsonify({"error": "No active analysis session."}), 409
    requested_session = request.args.get("session")
    if requested_session is not None and requested_session != str(session_id):
        return jsonify({"error": "The requested analysis session is no longer active."}), 409

    return Response(
        generate_frames(session_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ================= LIVE DATA API (UNCHANGED) =================
@app.route("/data")
def data():
    if os.path.exists("current_status.json"):
        with open("current_status.json", "r") as f:
            return jsonify(json.load(f))

    return jsonify({
        "time": "--",
        "blink_count": 0,
        "ear": 0,
        "pitch": 0,
        "yaw": 0,
        "roll": 0,
        "fatigue": "WAITING",
        "suggestion": "Waiting for face detection"
    })


# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(debug=True)