from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

import branding


class TitleBar(QWidget):
    def __init__(self, window, title="FaceTrack — Attendance System"):
        super().__init__(window)
        self.window_ref = window
        self.setObjectName("titleBar")
        self.setFixedHeight(46)
        self._drag = None

        icon = QLabel()
        icon.setPixmap(branding.app_icon_pixmap(18))
        icon.setFixedSize(18, 18)

        title_label = QLabel(title)
        title_label.setObjectName("tbTitle")

        self.min_btn = QPushButton("–")
        self.min_btn.setObjectName("tbMin")
        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("tbMax")
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("tbClose")

        for button in (self.min_btn, self.max_btn, self.close_btn):
            button.setFixedSize(34, 30)
            button.setFocusPolicy(Qt.NoFocus)
            button.setCursor(Qt.PointingHandCursor)

        self.min_btn.clicked.connect(window.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(window.close)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 12, 0)
        layout.setSpacing(10)
        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    def toggle_maximize(self):
        window = self.window_ref
        if window.isMaximized():
            window.showNormal()
            self.max_btn.setText("□")
        else:
            window.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag = (
                event.globalPosition().toPoint()
                - self.window_ref.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag is not None and not self.window_ref.isMaximized():
            self.window_ref.move(event.globalPosition().toPoint() - self._drag)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
        super().mouseDoubleClickEvent(event)