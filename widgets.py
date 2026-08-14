from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


def _soft_shadow(widget):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(38)
    shadow.setOffset(0, 10)
    shadow.setColor(QColor(0, 0, 0, 90))
    widget.setGraphicsEffect(shadow)


class NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("navButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)


class StatCard(QFrame):
    def __init__(self, caption, value="0", accent="#6d5efc", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        _soft_shadow(self)

        bar = QFrame()
        bar.setObjectName("statBar")
        bar.setFixedHeight(4)
        bar.setStyleSheet(
            f"QFrame#statBar {{ background: {accent}; border: none; border-radius: 2px; }}"
        )

        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")

        caption_label = QLabel(caption)
        caption_label.setObjectName("statCaption")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)
        layout.addWidget(bar)
        layout.addWidget(self.value_label)
        layout.addWidget(caption_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class ActionCard(QFrame):
    clicked = Signal()

    def __init__(self, title, subtitle, accent="#6d5efc", parent=None):
        super().__init__(parent)
        self.setObjectName("actionCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(128)
        self.setStyleSheet(
            f"QFrame#actionCard:hover {{ border-color: {accent}; background: #161F36; }}"
        )
        _soft_shadow(self)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("cardSub")
        subtitle_label.setWordWrap(True)

        chevron = QLabel("→")
        chevron.setObjectName("cardChevron")
        chevron.setStyleSheet(f"color: {accent};")

        text_col = QVBoxLayout()
        text_col.setSpacing(6)
        text_col.addWidget(title_label)
        text_col.addWidget(subtitle_label)

        row = QHBoxLayout()
        row.setSpacing(16)
        row.addLayout(text_col)
        row.addStretch()
        row.addWidget(chevron)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.addLayout(row)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class EmptyState(QFrame):
    def __init__(self, title, subtitle="", icon="◈", parent=None):
        super().__init__(parent)
        self.setObjectName("emptyState")

        icon_label = QLabel(icon)
        icon_label.setObjectName("emptyIcon")
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("emptyTitle")
        title_label.setAlignment(Qt.AlignCenter)

        sub_label = QLabel(subtitle)
        sub_label.setObjectName("emptySub")
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 26, 20, 26)
        layout.setSpacing(8)
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(sub_label)