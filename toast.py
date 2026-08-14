from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel


class Toast(QFrame):
    def __init__(self, message, accent="#6D5EFC", icon="✓", parent=None):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setAttribute(Qt.WA_StyledBackground, True)

        icon_label = QLabel(icon)
        icon_label.setObjectName("toastIcon")
        icon_label.setStyleSheet(f"color: {accent};")

        msg_label = QLabel(message)
        msg_label.setObjectName("toastMsg")
        msg_label.setWordWrap(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 18, 12)
        layout.setSpacing(10)
        layout.addWidget(icon_label, alignment=Qt.AlignTop)
        layout.addWidget(msg_label)

        self.setFixedWidth(330)
        self.adjustSize()