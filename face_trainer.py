import json
import shutil

import cv2
import numpy as np

from paths import DATA_DIR

FACES_DIR = DATA_DIR / "faces"
MODEL_PATH = DATA_DIR / "trainer.yml"
LABELS_PATH = DATA_DIR / "labels.json"
FACE_SIZE = (200, 200)


def load_face_cascade():
    local = DATA_DIR / "haarcascade_frontalface_default.xml"
    if local.exists():
        return cv2.CascadeClassifier(str(local))
    return cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )


def list_people():
    if not FACES_DIR.exists():
        return []
    return sorted(p.name for p in FACES_DIR.iterdir() if p.is_dir())


def count_photos(name):
    folder = FACES_DIR / name
    if not folder.exists():
        return 0
    return len(list(folder.glob("*.jpg")))


def delete_person(name):
    folder = FACES_DIR / name
    if not folder.exists():
        return False
    shutil.rmtree(folder)
    train_model()
    return True


def save_face_image(name, face_gray):
    folder = FACES_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    idx = len(list(folder.glob("*.jpg"))) + 1
    resized = cv2.resize(face_gray, FACE_SIZE)
    path = folder / f"img_{idx:03d}.jpg"
    cv2.imwrite(str(path), resized)
    return idx


def train_model():
    if not FACES_DIR.exists():
        return False
    images = []
    labels = []
    label_map = {}
    next_id = 0
    for folder in sorted(FACES_DIR.iterdir()):
        if not folder.is_dir():
            continue
        name = folder.name
        if name not in label_map:
            label_map[name] = next_id
            next_id += 1
        for img_path in sorted(folder.glob("*.jpg")):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(label_map[name])
    if not images:
        return False
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))
    recognizer.write(str(MODEL_PATH))
    LABELS_PATH.write_text(
        json.dumps({str(v): k for k, v in label_map.items()})
    )
    return True


def load_recognizer():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    if MODEL_PATH.exists():
        recognizer.read(str(MODEL_PATH))
    return recognizer


def get_name(label):
    if not LABELS_PATH.exists():
        return None
    mapping = json.loads(LABELS_PATH.read_text())
    return mapping.get(str(label))