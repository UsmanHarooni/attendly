import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal

import face_trainer


def available_cameras():
    indices = []
    for i in range(4):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            indices.append(i)
        cap.release()
    return indices


class CameraThread(QThread):
    frame_ready = Signal(np.ndarray, object)
    camera_failed = Signal()

    def __init__(self, camera_index=0, recognize=True, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.recognize = recognize
        self._running = True
        self.cascade = face_trainer.load_face_cascade()
        self.recognizer = face_trainer.load_recognizer() if recognize else None

    def run(self):
        try:
            self._run()
        except Exception:
            self.camera_failed.emit()

    def _run(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.camera_failed.emit()
            self._running = False
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while self._running:
            ok, frame = cap.read()
            if not ok:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            faces = self.cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
            )
            results = []
            for (x, y, w, h) in faces:
                name = None
                confidence = 0
                if self.recognize:
                    face = gray[y : y + h, x : x + w]
                    face = cv2.resize(face, face_trainer.FACE_SIZE)
                    label, confidence = self.recognizer.predict(face)
                    name = face_trainer.get_name(label) if label >= 0 else None
                results.append((x, y, w, h, name, confidence))
            self.frame_ready.emit(rgb, results)
            self.msleep(30)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()