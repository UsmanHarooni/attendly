from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

import settings


class PinDialog(QDialog):
    def __init__(self, parent=None, message="Enter the admin PIN to continue."):
        super().__init__(parent)
        self.setWindowTitle("Admin PIN")
        self.setMinimumWidth(340)

        label = QLabel(message)
        label.setObjectName("status")
        label.setWordWrap(True)

        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.Password)
        self.input.setPlaceholderText("PIN")
        self.input.setFixedHeight(40)
        self.input.returnPressed.connect(self.accept)

        self.ok_btn = QPushButton("Unlock")
        self.ok_btn.setObjectName("primary")
        self.cancel_btn = QPushButton("Cancel")

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.ok_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(label)
        layout.addWidget(self.input)
        layout.addLayout(buttons)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.input.setFocus()

    @staticmethod
    def prompt(parent=None, message="Enter the admin PIN to continue."):
        for _ in range(3):
            dialog = PinDialog(parent, message)
            if dialog.exec() != QDialog.Accepted:
                return False
            if settings.verify_admin_pin(dialog.input.text().strip()):
                return True
            QMessageBox.warning(parent, "Wrong PIN", "That PIN is incorrect. Try again.")
        return False


class PinChangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Admin PIN")
        self.setMinimumWidth(340)

        label = QLabel("Choose a new PIN (at least 4 characters).")
        label.setObjectName("status")
        label.setWordWrap(True)

        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        self.new_input.setPlaceholderText("New PIN")
        self.new_input.setFixedHeight(40)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirm new PIN")
        self.confirm_input.setFixedHeight(40)
        self.confirm_input.returnPressed.connect(self.accept)

        self.save_btn = QPushButton("Save PIN")
        self.save_btn.setObjectName("primary")
        self.cancel_btn = QPushButton("Cancel")

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.save_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(label)
        layout.addWidget(self.new_input)
        layout.addWidget(self.confirm_input)
        layout.addLayout(buttons)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.reject)
        self.new_input.setFocus()

    def save(self):
        new_pin = self.new_input.text().strip()
        confirm = self.confirm_input.text().strip()
        if len(new_pin) < 4:
            QMessageBox.warning(self, "Too short", "The PIN must be at least 4 characters.")
            return
        if new_pin != confirm:
            QMessageBox.warning(self, "No match", "The two PINs do not match.")
            return
        settings.set_admin_pin(new_pin)
        self.accept()