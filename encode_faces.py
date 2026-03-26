
import face_recognition
import cv2
import os
import pickle

STUDENT_IMG_DIR = " " #dataset name

def encode_faces():
    known_encodings = []
    known_ids = []

    for student_id in os.listdir(STUDENT_IMG_DIR):
        student_dir = os.path.join(STUDENT_IMG_DIR, student_id)
        if not os.path.isdir(student_dir):
            continue  # skip non-folder files

        for img_name in os.listdir(student_dir):
            img_path = os.path.join(student_dir, img_name)
            if not img_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue  # skip non-image files

            image = cv2.imread(img_path)
            if image is None:
                print(f"[WARNING] Cannot read image {img_path}")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            if len(encodings) == 0:
                print(f"[WARNING] No face found in {img_path}")
                continue

            for enc in encodings:
                known_encodings.append(enc)
                known_ids.append(student_id)
                print(f"[INFO] Encoded {img_path}")

    data = {"encodings": known_encodings, "ids": known_ids}
    with open("encodings.pickle", "wb") as f:
        pickle.dump(data, f)
    print("[INFO] Encodings saved to encodings.pickle")

if __name__ == "__main__":
    encode_faces()
