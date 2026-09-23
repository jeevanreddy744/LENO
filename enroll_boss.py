import os
import cv2
import numpy as np

SAMPLES = 100
FACE_SIZE = (200, 200)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FACE_DIR = os.path.join(DATA_DIR, "boss_faces")
MODEL_PATH = os.path.join(DATA_DIR, "boss_model.yml")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(FACE_DIR):
        for filename in os.listdir(FACE_DIR):
            path = os.path.join(FACE_DIR, filename)
            if os.path.isfile(path):
                os.remove(path)
    else:
        os.makedirs(FACE_DIR)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("❌ Could not open camera.")
        return

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    print("=" * 55)
    print("             LENO BOSS ENROLLMENT")
    print("=" * 55)
    print()
    print("Look at the camera.")
    print("Slowly move your head left, right, up and down.")
    print("Keep your face clearly visible.")
    print()
    print("Press Q to cancel.")
    print()

    count = 0

    while count < SAMPLES:
        success, frame = camera.read()

        if not success:
            print("❌ Could not read camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(100, 100)
        )

        if len(faces) > 0:
            x, y, w, h = max(
                faces,
                key=lambda face: face[2] * face[3]
            )

            face = gray[y:y + h, x:x + w]

            if face.size > 0:
                face = cv2.equalizeHist(face)
                face = cv2.resize(face, FACE_SIZE)

                filename = os.path.join(
                    FACE_DIR,
                    f"boss_{count:03d}.jpg"
                )

                cv2.imwrite(filename, face)
                count += 1

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Boss samples: {count}/{SAMPLES}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
        else:
            cv2.putText(
                frame,
                "Face not detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        cv2.imshow(
            "LENO - Boss Enrollment",
            frame
        )

        key = cv2.waitKey(100) & 0xFF

        if key == ord("q"):
            print("\n❌ Enrollment cancelled.")
            camera.release()
            cv2.destroyAllWindows()
            return

    camera.release()
    cv2.destroyAllWindows()

    print()
    print(f"✅ Captured {count} Boss samples.")
    print("🧠 Training Boss recognition model...")

    faces = []
    labels = []

    for filename in sorted(os.listdir(FACE_DIR)):
        path = os.path.join(FACE_DIR, filename)

        image = cv2.imread(
            path,
            cv2.IMREAD_GRAYSCALE
        )

        if image is None:
            continue

        image = cv2.resize(image, FACE_SIZE)

        faces.append(image)
        labels.append(1)

    if not faces:
        print("❌ No valid face samples found.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8
    )

    recognizer.train(
        faces,
        np.array(labels)
    )

    recognizer.write(MODEL_PATH)

    print()
    print("=" * 55)
    print("        ✅ BOSS ENROLLMENT COMPLETE")
    print("=" * 55)
    print(f"Samples: {len(faces)}")
    print(f"Model:   {MODEL_PATH}")
    print()
    print("You can now run:")
    print("python main.py")


if __name__ == "__main__":
    main()
