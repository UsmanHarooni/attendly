import time
from collections import Counter, deque

import cv2
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import database
import face_trainer
import settings
from camera import CameraThread, available_cameras

CONFIDENCE_THRESHOLD = 70
MARK_COOLDOWN_SECONDS = 10
VOTE_WINDOW = 12
VOTE_MAJORITY = 8

SESSION_MARKED = set()


class AttendanceWindow(QWidget):
    closed = Signal()
    marked = Signal(str)

    def __init__(self, parent=None, embedded=False):
        super().__init__(parent)
        self.embedded = embedded
        self.setWindowTitle("Take Attendance")
        self.setMinimumSize(880, 640)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) if embedded else layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)

        if not embedded:
            header = QLabel("Take Attendance")
            header.setObjectName("windowTitle")

            divider = QFrame()
            divider.setObjectName("divider")
            divider.setFixedHeight(1)

            layout.addWidget(header)
            layout.addWidget(divider)

        self.preview = QLabel("Camera off")
        self.preview.setObjectName("preview")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(360)

        self.status = QLabel("Press Start Scanning to begin.")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)

        self.cam_selector = QComboBox()
        self.cam_selector.setFixedWidth(150)
        self.refresh_cameras()

        self.start_btn = QPushButton("Start Scanning")
        self.start_btn.setObjectName("primary")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setEnabled(False)
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setObjectName("ghost")

        controls = QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(self.cam_selector)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.export_btn)

        self.manual_label = QLabel("No camera? Mark manually:")
        self.manual_label.setObjectName("status")
        self.manual_combo = QComboBox()
        self.manual_combo.setMinimumWidth(220)
        self.manual_btn = QPushButton("Mark Manually")
        self.manual_btn.setObjectName("ghost")

        manual = QHBoxLayout()
        manual.setSpacing(10)
        manual.addWidget(self.manual_label)
        manual.addWidget(self.manual_combo)
        manual.addWidget(self.manual_btn)
        manual.addStretch()

        self.filter_selector = QComboBox()
        self.filter_selector.setFixedWidth(150)
        self.filter_selector.currentIndexChanged.connect(self.refresh_table)

        self.class_selector = QComboBox()
        self.class_selector.setFixedWidth(150)
        self.class_selector.currentIndexChanged.connect(self.refresh_table)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Name", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        self.refresh_filters()

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self.class_selector, alignment=Qt.AlignLeft)
        right.addWidget(self.filter_selector, alignment=Qt.AlignLeft)
        right.addWidget(self.table)

        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(self.preview)
        left.addWidget(self.status)
        left.addLayout(controls)
        left.addLayout(manual)

        body = QHBoxLayout()
        body.setSpacing(16)
        body.addLayout(left, 3)
        body.addLayout(right, 2)

        layout.addLayout(body)

        self.camera = None
        self.last_marked = {}
        self.votes = deque(maxlen=VOTE_WINDOW)

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.export_btn.clicked.connect(self.export_csv)
        self.manual_btn.clicked.connect(self.mark_manually)

    def refresh_lists(self):
        self.refresh_filters()
        self.refresh_classes()
        self.refresh_manual()

    def refresh_cameras(self):
        self.cam_selector.clear()
        cams = available_cameras() or [0]
        for index in cams:
            self.cam_selector.addItem(f"Camera {index}", index)

    def refresh_classes(self):
        self.class_selector.blockSignals(True)
        current = self.class_selector.currentData()
        self.class_selector.clear()
        self.class_selector.addItem("All classes", "all")
        for class_name in database.get_classes():
            self.class_selector.addItem(class_name, class_name)
        if current is not None:
            index = self.class_selector.findData(current)
            if index >= 0:
                self.class_selector.setCurrentIndex(index)
        self.class_selector.blockSignals(False)

    def refresh_filters(self):
        self.filter_selector.blockSignals(True)
        current = self.filter_selector.currentData()
        self.filter_selector.clear()
        self.filter_selector.addItem("Today", "today")
        self.filter_selector.addItem("All records", "all")
        for name in face_trainer.list_people():
            self.filter_selector.addItem(name, name)
        if current is not None:
            index = self.filter_selector.findData(current)
            if index >= 0:
                self.filter_selector.setCurrentIndex(index)
        self.filter_selector.blockSignals(False)

    def refresh_manual(self):
        self.manual_combo.blockSignals(True)
        current = self.manual_combo.currentData()
        self.manual_combo.clear()
        unmarked = database.get_unmarked_today()
        self.manual_combo.addItem("Select student…", None)
        for name in unmarked:
            self.manual_combo.addItem(name, name)
        if current is not None:
            index = self.manual_combo.findData(current)
            if index >= 0:
                self.manual_combo.setCurrentIndex(index)
        self.manual_combo.blockSignals(False)
        self.manual_btn.setEnabled(bool(unmarked))

    def mark_manually(self):
        name = self.manual_combo.currentData()
        if not name:
            return
        ts, marked = database.mark_attendance(name)
        if marked:
            self.status.setText(f"Attendance marked manually for {name} at {ts}")
            self.marked.emit(f"Attendance marked manually for {name} at {ts}")
        else:
            self.status.setText(f"{name} was already marked today at {ts}")
        self.refresh_manual()
        self.refresh_table()

    def start_camera(self):
        if not face_trainer.list_people():
            QMessageBox.warning(
                self,
                "No people registered",
                "No people are registered yet. Register someone first.",
            )
            return
        index = self.cam_selector.currentData()
        self.camera = CameraThread(camera_index=index, parent=self)
        self.camera.frame_ready.connect(self.process_frame)
        self.camera.camera_failed.connect(self.camera_error)
        self.camera.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.cam_selector.setEnabled(False)
        self.status.setText("Scanning... look at the camera.")

    def camera_error(self):
        QMessageBox.critical(
            self, "Camera error", "Could not open the camera. Check it is connected."
        )
        self.close()

    def process_frame(self, frame, results):
        for (x, y, w, h, name, confidence) in results:
            if name and confidence <= CONFIDENCE_THRESHOLD:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{name} ({confidence:.0f})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                self.votes.append(name)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    "Unknown",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )
                self.votes.append(None)
        if results:
            self.check_votes()
        h, w, ch = frame.shape
        image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888).copy()
        self.preview.setPixmap(
            QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

    def check_votes(self):
        counts = Counter(name for name in self.votes if name)
        if not counts:
            return
        name, count = counts.most_common(1)[0]
        if count >= VOTE_MAJORITY:
            self.mark_if_due(name)

    def mark_if_due(self, name):
        now = time.time()
        if settings.get_marking_mode() == "session":
            if name in SESSION_MARKED:
                return
            SESSION_MARKED.add(name)
            ts, _ = database.mark_attendance(name)
            self.status.setText(f"Attendance marked for {name} at {ts}")
            self.marked.emit(f"Attendance marked for {name} at {ts}")
            self.refresh_table()
            return
        if (
            name in self.last_marked
            and now - self.last_marked[name] < MARK_COOLDOWN_SECONDS
        ):
            return
        self.last_marked[name] = now
        ts, marked = database.mark_attendance(name)
        if marked:
            self.status.setText(f"Attendance marked for {name} at {ts}")
            self.marked.emit(f"Attendance marked for {name} at {ts}")
        else:
            self.status.setText(f"{name} was already marked today at {ts}")
        self.refresh_table()

    def current_records(self):
        mode = self.filter_selector.currentData()
        class_name = self.class_selector.currentData()
        class_filter = class_name is not None and class_name != "all"
        if mode == "all":
            return (
                database.get_all_records_by_class(class_name)
                if class_filter
                else database.get_all_records()
            )
        if mode == "today":
            return (
                database.get_today_records_by_class(class_name)
                if class_filter
                else database.get_today_records()
            )
        if class_filter:
            return database.get_person_records_in_class(mode, class_name)
        return database.get_person_records(mode)

    def refresh_table(self):
        rows = self.current_records()
        self.table.setRowCount(len(rows))
        for i, (name, ts) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(ts))

    def export_csv(self):
        rows = self.current_records()
        if not rows:
            QMessageBox.information(self, "Nothing to export", "No records to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export attendance", "attendance.csv", "CSV files (*.csv)"
        )
        if not path:
            return
        database.export_records_to_csv(path, rows)
        QMessageBox.information(
            self, "Exported", f"Saved {len(rows)} records to\n{path}"
        )

    def stop_camera(self):
        if self.camera:
            self.camera.stop()
            self.camera = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.cam_selector.setEnabled(True)
        self.preview.clear()
        self.preview.setText("Camera off")
        self.status.setText("Scanning stopped.")

    def closeEvent(self, event):
        if self.camera:
            self.camera.stop()
        event.accept()
        self.closed.emit()