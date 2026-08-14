import cv2
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import database
import face_trainer
from camera import CameraThread

CAPTURE_INTERVAL_MS = 1500
TARGET_PHOTOS = 15


class RegisterWindow(QWidget):
    registered = Signal(str)

    def __init__(self, parent=None, embedded=False):
        super().__init__(parent)
        self.embedded = embedded
        self.setWindowTitle("Register New Person")
        self.setMinimumSize(760, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) if embedded else layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)

        if not embedded:
            header = QLabel("Register New Person")
            header.setObjectName("windowTitle")

            divider = QFrame()
            divider.setObjectName("divider")
            divider.setFixedHeight(1)

            layout.addWidget(header)
            layout.addWidget(divider)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter student's full name")
        self.name_input.setFixedHeight(40)

        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Class (e.g. 8A)")
        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("Section")
        self.roll_input = QLineEdit()
        self.roll_input.setPlaceholderText("Roll No")

        class_row = QHBoxLayout()
        class_row.setSpacing(10)
        class_row.addWidget(self.class_input, 2)
        class_row.addWidget(self.section_input, 1)
        class_row.addWidget(self.roll_input, 1)

        self.preview = QLabel("Camera off")
        self.preview.setObjectName("preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(360)

        self.status = QLabel(
            "Turn your head slowly left and right while photos are taken automatically."
        )
        self.status.setObjectName("status")
        self.status.setWordWrap(True)

        self.start_btn = QPushButton("Start Camera")
        self.start_btn.setObjectName("primary")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setEnabled(False)
        self.finish_btn = QPushButton("Finish & Save")
        self.finish_btn.setObjectName("success")
        self.finish_btn.setEnabled(False)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(self.start_btn)
        buttons.addWidget(self.stop_btn)
        buttons.addWidget(self.finish_btn)

        layout.addWidget(self.name_input)
        layout.addLayout(class_row)
        layout.addWidget(self.preview)
        layout.addWidget(self.status)
        layout.addLayout(buttons)

        self.camera = None
        self.capture_timer = QTimer(self)
        self.capture_timer.setInterval(CAPTURE_INTERVAL_MS)
        self.capture_timer.timeout.connect(self.capture_photo)
        self.count = 0

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.finish_btn.clicked.connect(self.finish)

    def start_camera(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Name required", "Please enter a name first.")
            return
        if name in face_trainer.list_people():
            answer = QMessageBox.question(
                self,
                "Already registered",
                f"{name} is already registered. Add more photos anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
        self.name_input.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.finish_btn.setEnabled(True)
        self.status.setText(
            f"Turn your head slowly left and right. Aim for {TARGET_PHOTOS} photos."
        )

        self.camera = CameraThread(recognize=False, parent=self)
        self.camera.frame_ready.connect(self.process_frame)
        self.camera.camera_failed.connect(self.camera_error)
        self.camera.start()
        self.capture_timer.start()

    def stop_camera(self):
        self.capture_timer.stop()
        if self.camera:
            self.camera.stop()
            self.camera = None
        self.reset_ui()
        self.status.setText("Capture stopped. Start again whenever you are ready.")

    def camera_error(self):
        QMessageBox.critical(
            self, "Camera error", "Could not open the camera. Check it is connected."
        )
        self.close()

    def process_frame(self, frame, results):
        self.last_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        self.last_results = results
        for (x, y, w, h, name, confidence) in results:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        h, w, ch = frame.shape
        image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.preview.setPixmap(
            QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

    def capture_photo(self):
        if not hasattr(self, "last_results") or len(self.last_results) == 0:
            self.status.setText(
                f"No face detected yet. Look at the camera and turn your head slowly. "
                f"Photos captured: {self.count}/{TARGET_PHOTOS}"
            )
            return
        x, y, w, h = self.last_results[0][:4]
        face = self.last_gray[y : y + h, x : x + w]
        idx = face_trainer.save_face_image(self.name_input.text().strip(), face)
        self.count += 1
        self.status.setText(
            f"Photo {idx} saved. Keep turning your head slowly. "
            f"Photos captured: {self.count}/{TARGET_PHOTOS}"
        )

    def finish(self):
        if self.count == 0:
            QMessageBox.warning(
                self,
                "No photos",
                "No face photos were captured. Make sure your face is visible.",
            )
            return
        self.capture_timer.stop()
        if self.camera:
            self.camera.stop()
            self.camera = None
        if face_trainer.train_model():
            name = self.name_input.text().strip()
            class_name = self.class_input.text().strip()
            section = self.section_input.text().strip()
            roll_no = self.roll_input.text().strip()
            if database.get_student(name):
                database.update_student(
                    name, class_name=class_name, section=section, roll_no=roll_no
                )
            else:
                database.add_student(name, class_name, section, roll_no)
            self.registered.emit(f"{name} registered with {self.count} photos")
            if self.embedded:
                self.reset_ui()
            else:
                self.close()
        else:
            QMessageBox.critical(self, "Error", "Could not train the model.")

    def reset_ui(self):
        self.count = 0
        self.name_input.clear()
        self.name_input.setEnabled(True)
        self.class_input.clear()
        self.section_input.clear()
        self.roll_input.clear()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.finish_btn.setEnabled(False)
        self.status.setText(
            "Turn your head slowly left and right while photos are taken automatically."
        )
        self.preview.clear()
        self.preview.setText("Camera off")
        if hasattr(self, "last_results"):
            del self.last_results

    def closeEvent(self, event):
        if self.camera:
            self.camera.stop()
        event.accept()