from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import database
import settings
from pin_dialog import PinChangeDialog, PinDialog


class SettingsWindow(QWidget):
    saved = Signal(str)

    def __init__(self, parent=None, embedded=False):
        super().__init__(parent)
        self.embedded = embedded
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) if embedded else layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)

        if not embedded:
            header = QLabel("Settings")
            header.setObjectName("windowTitle")

            divider = QFrame()
            divider.setObjectName("divider")
            divider.setFixedHeight(1)

            layout.addWidget(header)
            layout.addWidget(divider)

        # -------------------------------------------------- marking mode

        mode_label = QLabel("Attendance marking rule")
        mode_label.setObjectName("panelTitle")

        self.mode_combo = QComboBox()
        self.mode_combo.setFixedWidth(280)
        self.mode_combo.addItem("Once per day", "daily")
        self.mode_combo.addItem("Once per app session", "session")
        index = self.mode_combo.findData(settings.get_marking_mode())
        self.mode_combo.setCurrentIndex(max(index, 0))

        self.desc = QLabel("")
        self.desc.setObjectName("status")
        self.desc.setWordWrap(True)
        self.update_desc()
        self.mode_combo.currentIndexChanged.connect(self.update_desc)

        self.mode_save_btn = QPushButton("Save")
        self.mode_save_btn.setObjectName("primary")

        layout.addWidget(mode_label)
        layout.addWidget(self.mode_combo)
        layout.addWidget(self.desc)
        layout.addWidget(self.mode_save_btn, alignment=Qt.AlignRight)

        layout.addSpacing(6)

        # -------------------------------------------------------- PIN

        pin_label = QLabel("Admin PIN")
        pin_label.setObjectName("panelTitle")

        pin_desc = QLabel(
            "The PIN unlocks FaceTrack and protects settings, students and logs."
        )
        pin_desc.setObjectName("status")
        pin_desc.setWordWrap(True)

        self.pin_btn = QPushButton("Change PIN")
        self.pin_btn.setObjectName("ghost")

        layout.addWidget(pin_label)
        layout.addWidget(pin_desc)
        layout.addWidget(self.pin_btn, alignment=Qt.AlignLeft)

        layout.addSpacing(6)

        # -------------------------------------------------------- backup

        data_label = QLabel("Data backup")
        data_label.setObjectName("panelTitle")

        data_desc = QLabel(
            "A backup is taken automatically once a day. Backups are stored in "
            "the data folder."
        )
        data_desc.setObjectName("status")
        data_desc.setWordWrap(True)

        self.backup_btn = QPushButton("Back up now")
        self.backup_btn.setObjectName("ghost")
        self.restore_btn = QPushButton("Restore from backup")
        self.restore_btn.setObjectName("ghost")

        data_row = QHBoxLayout()
        data_row.setSpacing(10)
        data_row.addWidget(self.backup_btn)
        data_row.addWidget(self.restore_btn)
        data_row.addStretch()

        layout.addWidget(data_label)
        layout.addWidget(data_desc)
        layout.addLayout(data_row)
        layout.addStretch()

        self.mode_save_btn.clicked.connect(self.save_mode)
        self.pin_btn.clicked.connect(self.change_pin)
        self.backup_btn.clicked.connect(self.backup_now)
        self.restore_btn.clicked.connect(self.restore_backup)

    def update_desc(self):
        if self.mode_combo.currentData() == "daily":
            self.desc.setText(
                "Each person is marked present once per day. "
                "Closing and reopening the app does not create a second record."
            )
        else:
            self.desc.setText(
                "Each person is marked once per app session. "
                "Closing and reopening the app lets them be marked again."
            )

    def save_mode(self):
        settings.set_marking_mode(self.mode_combo.currentData())
        self.saved.emit("Attendance rule updated")

    def change_pin(self):
        if not PinDialog.prompt(
            self, "Enter the current PIN to change it."
        ):
            return
        dialog = PinChangeDialog(self)
        if dialog.exec() == PinChangeDialog.Accepted:
            self.saved.emit("Admin PIN updated")

    def backup_now(self):
        try:
            path = database.backup_data()
        except OSError as exc:
            QMessageBox.critical(self, "Backup failed", str(exc))
            return
        self.saved.emit(f"Backup saved to {path.name}")

    def restore_backup(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Restore from backup", "", "Database files (*.db)"
        )
        if not path:
            return
        answer = QMessageBox.question(
            self,
            "Restore database",
            "This replaces all current attendance data with the backup.\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            database.restore_database(path)
        except OSError as exc:
            QMessageBox.critical(self, "Restore failed", str(exc))
            return
        self.saved.emit("Database restored from backup")