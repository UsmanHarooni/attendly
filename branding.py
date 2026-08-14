from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QIcon,
    QLinearGradient,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

VERSION = "v1.3.0"
SPLASH_STEPS = [
    "Loading recognition engine…",
    "Warming up the camera…",
    "Finalizing interface…",
]


def app_icon_pixmap(size=256):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor("#6D5EFC"))
    grad.setColorAt(1, QColor("#8B5CF6"))
    p.setPen(Qt.NoPen)
    p.setBrush(grad)
    p.drawRoundedRect(QRectF(0, 0, size, size), size * 0.22, size * 0.22)
    p.setPen(QColor("#FFFFFF"))
    font = QFont("Inter", int(size * 0.34))
    font.setWeight(QFont.ExtraBold)
    p.setFont(font)
    p.drawText(QRectF(0, 0, size, size), Qt.AlignCenter, "FT")
    p.end()
    return pm


def app_icon():
    return QIcon(app_icon_pixmap(256))


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(340, 400)

        card = QFrame()
        card.setObjectName("splashCard")

        badge = QLabel()
        badge.setPixmap(app_icon_pixmap(84))
        badge.setAlignment(Qt.AlignCenter)

        title = QLabel("Attendly")
        title.setObjectName("splashTitle")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("ATTENDANCE SUITE")
        sub.setObjectName("logoSub")
        sub.setAlignment(Qt.AlignCenter)

        version = QLabel(VERSION)
        version.setObjectName("splashVersion")
        version.setAlignment(Qt.AlignCenter)

        self.status = QLabel(SPLASH_STEPS[0])
        self.status.setObjectName("splashStatus")
        self.status.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 44, 40, 36)
        layout.setSpacing(10)
        layout.addWidget(badge)
        layout.addSpacing(6)
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(8)
        layout.addWidget(version)
        layout.addStretch()
        layout.addWidget(self.status)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

        self._step = 0
        self._timer = QTimer(self)
        self._timer.setInterval(380)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    def _advance(self):
        self._step += 1
        self.status.setText(SPLASH_STEPS[self._step % len(SPLASH_STEPS)])

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.center() - self.rect().center())