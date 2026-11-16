import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import cv2
import numpy as np
import os
import csv
import smtplib
import time

from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path

# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

env_path = Path(__file__).resolve().parent / ".env"

if env_path.is_file():
    with open(env_path, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, separator, value = line.partition("=")

            if separator:
                os.environ.setdefault(
                    key.strip(),
                    value.strip().strip('"').strip("'")
                )


# ==========================================
# CONFIGURATION
# ==========================================

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

KNOWN_FACES_DIR = "known_faces"
ATTENDANCE_FILE = "attendance.csv"

CASCADE_PATH = "models/haarcascade_frontalface_default.xml"

COOLDOWN_SECONDS = 30

# LBPH confidence threshold.
# Lower confidence means a better match.
FACE_CONFIDENCE_THRESHOLD = 70
CAMERA_INDEX = 1
FACE_WIDTH = 200
FACE_HEIGHT = 200
# ==========================================
# INITIALIZE OPENCV
# ==========================================
face_detector = cv2.CascadeClassifier(CASCADE_PATH)

if face_detector.empty():
    raise RuntimeError("Could not load Haar Cascade model.")


# ==========================================
# FACE PREPROCESSING
# ==========================================

def preprocess_face(face):

    face = cv2.resize(
        face,
        (FACE_WIDTH, FACE_HEIGHT)
    )

    face = cv2.equalizeHist(face)

    return face


def detect_largest_face(gray_image):

    faces = face_detector.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(faces) == 0:
        return None

    # Select the largest detected face.
    x, y, w, h = max(
        faces,
        key=lambda face: face[2] * face[3]
    )

    return x, y, w, h


# ==========================================
# LOAD AND TRAIN KNOWN FACES
# ==========================================

def load_known_faces():

    training_faces = []
    training_labels = []

    label_to_name = {}

    if not os.path.isdir(KNOWN_FACES_DIR):
        print("[ERROR] known_faces directory not found.")
        return None, {}

    current_label = 0

    for filename in sorted(os.listdir(KNOWN_FACES_DIR)):

        if not filename.lower().endswith(
            (".jpg", ".jpeg", ".png")
        ):
            continue

        path = os.path.join(
            KNOWN_FACES_DIR,
            filename
        )

        try:

            # john_1.jpg and john_2.jpg -> John
            name_part = os.path.splitext(filename)[0]

            parts = name_part.rsplit("_", 1)

            if len(parts) == 2 and parts[1].isdigit():
                name_part = parts[0]

            name = name_part.replace("_", " ").title()

            image = cv2.imread(path)

            if image is None:
                print(f"[WARNING] Cannot read {filename}")
                continue

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            face_location = detect_largest_face(gray)

            if face_location is None:
                print(f"[WARNING] No face found in {filename}")
                continue

            x, y, w, h = face_location

            face = gray[y:y+h, x:x+w]

            face = preprocess_face(face)

            # Assign one label per person.
            if name not in label_to_name:

                label_to_name[name] = current_label

                current_label += 1

            label = label_to_name[name]

            training_faces.append(face)
            training_labels.append(label)

            print(f"[INFO] Loaded {filename} -> {name}")

        except Exception as e:

            print(f"[ERROR] Failed to load {filename}: {e}")

    if not training_faces:
        return None, {}

    # Create LBPH recognizer.
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8
    )

    recognizer.train(
        training_faces,
        np.array(training_labels, dtype=np.int32)
    )

    print("[INFO] Face training completed.")

    return recognizer, {
        label: name
        for name, label in label_to_name.items()
    }

def mark_attendance(name):

    today = date.today().isoformat()

    if os.path.exists(ATTENDANCE_FILE):

        try:

            with open(
                ATTENDANCE_FILE,
                "r",
                newline="",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:

                    if (
                        row.get("Name") == name
                        and row.get("Date") == today
                    ):
                        return False

        except (OSError, csv.Error) as e:

            print(f"[ERROR] Attendance read failed: {e}")
            return False

    current_time = datetime.now().strftime("%H:%M:%S")

    file_exists = (
        os.path.exists(ATTENDANCE_FILE)
        and os.path.getsize(ATTENDANCE_FILE) > 0
    )

    try:

        with open(
            ATTENDANCE_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    "Name",
                    "Date",
                    "Time",
                    "Status"
                ])

            writer.writerow([
                name,
                today,
                current_time,
                "Present"
            ])

        print(
            f"[ATTENDANCE] {name} marked present at {current_time}"
        )

        return True

    except OSError as e:

        print(f"[ERROR] Attendance write failed: {e}")
        return False


# ==========================================
# EMAIL ALERT
# ==========================================

def send_email_alert(image_frame):

    if not SENDER_PASSWORD:

        print("[ERROR] Email password not configured.")
        time.sleep(0.03)
        return False

    try:

        success, encoded_image = cv2.imencode(
            ".jpg",
            image_frame
        )

        if not success:
            return False

        image_bytes = encoded_image.tobytes()

        msg = MIMEMultipart()

        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        msg["Subject"] = "ALERT: Unauthorized Person Detected!"

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        body = (
            "An unknown face was detected.\n\n"
            f"Detection time: {timestamp}\n"
            "Captured image is attached."
        )

        msg.attach(MIMEText(body, "plain"))

        attachment = MIMEImage(
            image_bytes,
            _subtype="jpeg",
            name="unauthorized_detected.jpg"
        )

        msg.attach(attachment)

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=20
        ) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                SENDER_EMAIL,
                SENDER_PASSWORD
            )

            server.sendmail(
                SENDER_EMAIL,
                [RECEIVER_EMAIL],
                msg.as_string()
            )

        print("[SUCCESS] Alert email sent.")

        return True

    except Exception as e:

        print(f"[ERROR] Email failed: {e}")
        return False


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():
    recognizer, label_to_name = load_known_faces()
    if recognizer is None:
        print("[ERROR] No usable authorized faces.")
        return
    video_capture = cv2.VideoCapture(CAMERA_INDEX)
    if not video_capture.isOpened():
        print("[ERROR] Could not open camera.")
        return
    last_alert_time = 0.0
    attendance_marked_this_session = set()
    print("[INFO] Smart Attendance System started.")
    print("[INFO] Running in headless mode.")
    print("[INFO] Press Ctrl+C to stop.")
    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("[ERROR] Camera frame unavailable.")
                break
            # Downsample for performance.
            small_frame = cv2.resize(
                frame,
                (0, 0),
                fx=0.5,
                fy=0.5
            )
            gray = cv2.cvtColor(
                small_frame,
                cv2.COLOR_BGR2GRAY
            )
            detected_faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(40, 40)
            )
            current_time = time.time()
            unauthorized_detected = False
            for (x, y, w, h) in detected_faces:
                face = gray[y:y+h, x:x+w]
                face = preprocess_face(face)
                label, confidence = recognizer.predict(face)
                name = "UNAUTHORIZED"
                if (
                    confidence < FACE_CONFIDENCE_THRESHOLD
                    and label in label_to_name
                ):
                    name = label_to_name[label]
                if name == "UNAUTHORIZED":
                    unauthorized_detected = True
                else:
                    if name not in attendance_marked_this_session:
                        mark_attendance(name)
                        attendance_marked_this_session.add(name)
                    print(
                        f"[RECOGNIZED] {name} "
                        f"(Confidence: {confidence:.2f})"
                    )
            # Send only one alert per cooldown period.
            if unauthorized_detected:
                if current_time - last_alert_time >= COOLDOWN_SECONDS:
                    print("[ALERT] Unauthorized person detected!")
                    if send_email_alert(frame):
                        last_alert_time = current_time
            time.sleep(0.03)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping application...")
    finally:
        video_capture.release()
        print("[INFO] Camera released.")
        print("[INFO] Smart Attendance System stopped.")
if __name__ == "__main__":
    main()