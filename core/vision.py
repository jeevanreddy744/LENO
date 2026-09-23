import os

import cv2
from deepface import DeepFace


class LenoVision:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open the camera.")

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            "haarcascade_frontalface_default.xml"
        )

        if self.face_cascade.empty():
            raise RuntimeError("Could not load Haar face detector.")

        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1,
            neighbors=8,
            grid_x=8,
            grid_y=8
        )

        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "boss_model.yml"
        )

        if not os.path.exists(self.model_path):
            raise RuntimeError(
                "Boss face model not found. "
                "Run enroll_boss.py first."
            )

        self.recognizer.read(self.model_path)

        self.last_expression = "neutral"

    def get_current_person(self):
        success, frame = self.camera.read()

        if not success:
            return None

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Improve detection in different lighting conditions.
        gray = cv2.equalizeHist(gray)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=4,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0:
            return None

        # Use the largest face.
        x, y, w, h = max(
            faces,
            key=lambda item: item[2] * item[3]
        )

        face_image = gray[
            y:y + h,
            x:x + w
        ]

        if face_image.size == 0:
            return None

        face_for_recognition = cv2.resize(
            face_image,
            (200, 200)
        )

        label, confidence = self.recognizer.predict(
            face_for_recognition
        )

        # Strict enough to avoid casually identifying guests as Boss.
        if label == 1 and confidence < 50:
            is_boss = True
            name = "Boss"
        else:
            is_boss = False
            name = None

        expression = self.detect_expression(
            frame,
            x,
            y,
            w,
            h
        )

        return {
            "name": name,
            "is_boss": is_boss,
            "confidence": confidence,
            "expression": expression
        }

    def detect_expression(self, frame, x, y, w, h):
        try:
            face = frame[
                y:y + h,
                x:x + w
            ]

            if face.size == 0:
                return self.last_expression

            result = DeepFace.analyze(
                face,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="opencv"
            )

            if isinstance(result, list):
                result = result[0]

            emotions = result.get("emotion", {})

            if not emotions:
                return self.last_expression

            expression = max(
                emotions,
                key=emotions.get
            )

            expression_map = {
                "happy": "happy",
                "neutral": "neutral",
                "surprise": "surprised",
                "sad": "sad",
                "angry": "angry",
                "fear": "confused",
                "disgust": "confused"
            }

            detected_expression = expression_map.get(
                expression,
                "neutral"
            )

            self.last_expression = detected_expression

            return detected_expression

        except Exception:
            return self.last_expression

    def close(self):
        self.camera.release()
        cv2.destroyAllWindows()