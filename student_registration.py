import cv2
import os
import re
from db_utils import get_db_connection, create_tables

STUDENT_IMG_DIR = "dataset/"

def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def student_exists(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id=%s", (student_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def capture_face_images(student_id, name):
    cam = cv2.VideoCapture(0)
    count = 0
    student_dir = os.path.join(STUDENT_IMG_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)

    print("[INFO] Capturing images...")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        cv2.imshow("Register Face - Press 'q' to stop", frame)
        img_name = f"{student_dir}/{count}.jpg"
        cv2.imwrite(img_name, frame)
        count += 1

        if cv2.waitKey(100) & 0xFF == ord('q') or count >= 20:
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Captured {count} images for {name}")

def register_student(student_id, name, email):
    if not valid_email(email):
        print("Invalid email!")
        return
    if student_exists(student_id):
        print("Student already exists!")
        return

    capture_face_images(student_id, name)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (student_id, name, email, img_path) VALUES (%s, %s, %s, %s)",
                   (student_id, name, email, os.path.join(STUDENT_IMG_DIR, student_id)))
    conn.commit()
    conn.close()
    print(f"[INFO] Student {name} registered successfully.")

if __name__ == "__main__":
    create_tables()
    sid = input("Enter Student ID: ")
    name = input("Enter Name: ")
    email = input("Enter Parent Email: ")
    register_student(sid, name, email)
