
import cv2
import face_recognition
import os
import pickle
import numpy as np
from datetime import datetime, timedelta
from db_utils import get_db_connection
import time as t

# --- Configuration ---
PERIODS = {
    "Period 1": ("14:39", "14:41"),
    "Period 2": ("10:00", "10:50"),
    "Period 3": ("11:00", "11:56"),
    "Period 4": ("12:00", "12:58"),
    "Period 5": ("18:10", "18:18"),
}

CAMERA_INDEX = 0  # Laptop webcam

# --- Load Known Encodings ---
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

known_faces = data["encodings"]
known_ids = data["ids"]

# --- Helper Functions ---
def is_last_10_minutes(period_end):
    now = datetime.now().time()
    end_time = datetime.strptime(period_end, "%H:%M").time()
    end_minus_10 = (datetime.combine(datetime.today(), end_time) - timedelta(minutes=10)).time()
    return end_minus_10 <= now <= end_time

def mark_attendance(recognized_students, period_name):
    db = get_db_connection()
    cursor = db.cursor()
    date_today = datetime.now().date()

    # Mark present students
    for student_id in recognized_students:
        cursor.execute("""
            INSERT INTO attendance (student_id, period, date, status)
            VALUES (%s, %s, %s, %s)
        """, (student_id, period_name, date_today, "P"))

    # Mark absent students
    all_students = set(known_ids)
    absentees = all_students - set(recognized_students)
    for student_id in absentees:
        cursor.execute("""
            INSERT INTO attendance (student_id, period, date, status)
            VALUES (%s, %s, %s, %s)
        """, (student_id, period_name, date_today, "A"))

    db.commit()
    db.close()
    print(f"[INFO] Attendance recorded for {period_name} ✅")

def run_face_recognition(duration_seconds=60):  # <-- Changed to 1 minute
    cap = cv2.VideoCapture(CAMERA_INDEX)
    recognized = set()
    start_time = datetime.now()
    
    while (datetime.now() - start_time).seconds < duration_seconds:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            face_distances = face_recognition.face_distance(known_faces, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                recognized.add(known_ids[best_match_index])
    cap.release()
    return recognized

# --- Main Loop ---
processed_periods = set()

while True:
    now_str = datetime.now().strftime("%H:%M")
    for period_name, (start, end) in PERIODS.items():
        if is_last_10_minutes(end) and period_name not in processed_periods:
            print(f"[INFO] Taking attendance for {period_name} at {now_str} (1 min test)...")
            recognized_students = run_face_recognition(duration_seconds=60)  # 1 minute test
            mark_attendance(recognized_students, period_name)
            processed_periods.add(period_name)
    t.sleep(10)  # check every 10 seconds for quicker testing
