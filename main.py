import sys
from datetime import datetime

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import QDate, QEasingCurve, QMargins, QPoint, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import branding
import database
import face_trainer
import settings as settings_module
import theme
from attendance_window import AttendanceWindow
from logs_window import LogsPage
from manage_window import ManageWindow
from pin_dialog import PinDialog
from register_window import RegisterWindow
from reports_window import ReportsPage
from settings_window import SettingsWindow
from titlebar import TitleBar
from toast import Toast
from widgets import ActionCard, EmptyState, NavButton, StatCard

LOCKED_PAGES = {3, 4, 6}


class PageHeader(QWidget):
    def __init__(self, title, subtitle="", parent=None):
        super().__init__(parent)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("pageTitle")

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("pageSub")

        self.clock_label = QLabel("")
        self.clock_label.setObjectName("clock")

        self.date_label = QLabel("")
        self.date_label.setObjectName("dateLabel")
        self.date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        left = QVBoxLayout()
        left.setSpacing(2)
        left.addWidget(self.title_label)
        left.addWidget(self.subtitle_label)

        right = QVBoxLayout()
        right.setSpacing(1)
        right.addWidget(self.clock_label, alignment=Qt.AlignRight)
        right.addWidget(self.date_label, alignment=Qt.AlignRight)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(left)
        layout.addStretch()
        layout.addLayout(right)

    def tick(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %d %B %Y"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendly — Attendance System")
        self.setWindowIcon(branding.app_icon())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1180, 780)

        self.headers = []
        self._toast = None

        self.attendance_page = AttendanceWindow(embedded=True)
        self.register_page = RegisterWindow(embedded=True)
        self.manage_page = ManageWindow(embedded=True)
        self.logs_page = LogsPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsWindow(embedded=True)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.build_dashboard())
        self.stack.addWidget(
            self.make_page(
                self.attendance_page,
                "Take Attendance",
                "Scan faces, or mark students manually when the camera can't.",
            )
        )
        self.stack.addWidget(
            self.make_page(
                self.register_page,
                "Register Person",
                "Capture face photos to add a new person to the system.",
            )
        )
        self.stack.addWidget(
            self.make_page(
                self.manage_page,
                "Students",
                "Manage the roster: add, edit, import and remove students.",
            )
        )
        self.stack.addWidget(
            self.make_page(
                self.logs_page,
                "Logs & Reports",
                "Browse, export, or clear attendance logs by date.",
            )
        )
        self.stack.addWidget(
            self.make_page(
                self.reports_page,
                "Reports",
                "Daily reports, absent lists and monthly summaries — CSV or PDF.",
            )
        )
        self.stack.addWidget(
            self.make_page(
                self.settings_page,
                "Settings",
                "Configure marking rules, the admin PIN and backups.",
            )
        )

        sidebar = self.build_sidebar()

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(sidebar)
        body.addWidget(self.stack, 1)

        content = QWidget()
        content.setLayout(body)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(TitleBar(self))
        root.addWidget(content, 1)

        frame = QFrame()
        frame.setObjectName("windowBody")
        frame.setLayout(root)
        self.setCentralWidget(frame)

        self.stack.currentChanged.connect(self.on_page_changed)
        self.on_page_changed(0)

        self.attendance_page.marked.connect(
            lambda msg: self.toast(msg, accent="#10B981")
        )
        self.logs_page.logs_changed.connect(lambda msg: self.toast(msg))
        self.logs_page.logs_changed.connect(self.refresh_dashboard)
        self.register_page.registered.connect(
            lambda msg: self.toast(msg, accent="#10B981")
        )
        self.register_page.registered.connect(self.refresh_dashboard)
        self.register_page.registered.connect(self.manage_page.refresh_table)
        self.manage_page.people_updated.connect(
            lambda msg: self.toast(msg, accent="#10B981")
        )
        self.manage_page.people_updated.connect(self.refresh_dashboard)
        self.settings_page.saved.connect(lambda msg: self.toast(msg))

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self.tick_all)
        self.tick_all()
        self.clock_timer.start()

    # ------------------------------------------------------------ locking

    def navigate(self, index):
        if index in LOCKED_PAGES:
            if not PinDialog.prompt(
                self, "This area is protected. Enter the admin PIN to continue."
            ):
                return
        self.stack.setCurrentIndex(index)

    # -------------------------------------------------------------- toasts

    def toast(self, message, accent="#6D5EFC", icon="✓"):
        if self._toast is not None:
            self._toast.close()
        toast = Toast(message, accent=accent, icon=icon, parent=self)
        self._toast = toast
        x = self.width() - toast.width() - 24
        y = 56
        toast.move(x + 30, y)
        toast.show()
        animation = QPropertyAnimation(toast, b"pos", toast)
        animation.setDuration(220)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.setStartValue(toast.pos())
        animation.setEndValue(QPoint(x, y))
        animation.start()
        QTimer.singleShot(3200, toast.close)

    # ------------------------------------------------------------- sidebar

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(244)

        badge = QLabel()
        badge.setPixmap(branding.app_icon_pixmap(40))
        badge.setFixedSize(40, 40)

        logo_title = QLabel(
            '<span style="color:#F1F5F9;">Face</span>'
            '<span style="color:#8B5CF6;">Track</span>'
        )
        logo_title.setObjectName("logoTitle")
        logo_title.setTextFormat(Qt.RichText)

        logo_sub = QLabel("ATTENDANCE SUITE")
        logo_sub.setObjectName("logoSub")

        logo_text = QVBoxLayout()
        logo_text.setSpacing(0)
        logo_text.addWidget(logo_title)
        logo_text.addWidget(logo_sub)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)
        logo_row.addWidget(badge)
        logo_row.addLayout(logo_text)
        logo_row.addStretch()

        section = QLabel("MAIN MENU")
        section.setObjectName("navSection")

        entries = [
            ("◈", "Dashboard"),
            ("◎", "Take Attendance"),
            ("✚", "Register Person"),
            ("☰", "Students"),
            ("▤", "Logs & Reports"),
            ("🖶", "Reports"),
            ("⚙", "Settings"),
        ]
        self.nav_buttons = [NavButton(f"{icon}  {text}") for icon, text in entries]

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        for i, btn in enumerate(self.nav_buttons):
            self.nav_group.addButton(btn, i)
            btn.clicked.connect(lambda _checked=False, i=i: self.navigate(i))

        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(4)
        nav_layout.addWidget(section)
        for btn in self.nav_buttons:
            nav_layout.addWidget(btn)
        nav_layout.addStretch()

        footer_chip = QLabel(branding.VERSION)
        footer_chip.setObjectName("versionChip")
        footer_chip.setAlignment(Qt.AlignCenter)

        footer_text = QLabel("Face recognition powered by\nOpenCV · LBPH")
        footer_text.setObjectName("footerText")
        footer_text.setAlignment(Qt.AlignCenter)
        footer_text.setWordWrap(True)

        footer = QVBoxLayout()
        footer.setSpacing(8)
        footer.addWidget(footer_chip, alignment=Qt.AlignCenter)
        footer.addWidget(footer_text)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(18)
        layout.addLayout(logo_row)
        layout.addSpacing(6)
        layout.addLayout(nav_layout)
        layout.addLayout(footer)
        return sidebar

    # --------------------------------------------------------------- pages

    def make_page(self, widget, title, subtitle):
        page = QWidget()
        header = PageHeader(title, subtitle)
        self.headers.append(header)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 22, 30, 26)
        layout.setSpacing(16)
        layout.addWidget(header)
        layout.addWidget(widget)
        return page

    def build_dashboard(self):
        page = QWidget()
        header = PageHeader(
            "Dashboard",
            "Welcome back — here is today's attendance overview.",
        )
        self.headers.append(header)

        self.present_card = StatCard("Present today", "0", accent="#10B981")
        self.absent_card = StatCard("Absent today", "0", accent="#EF4444")
        self.registered_card = StatCard("Students on roster", "0", accent="#8B5CF6")
        self.rate_card = StatCard("Attendance rate", "0%", accent="#F59E0B")

        stats = QHBoxLayout()
        stats.setSpacing(14)
        for card in (
            self.present_card,
            self.absent_card,
            self.registered_card,
            self.rate_card,
        ):
            stats.addWidget(card, 1)

        self.attendance_card = ActionCard(
            "Take Attendance",
            "Scan faces and mark who is present today",
            accent="#8B5CF6",
        )
        self.register_card = ActionCard(
            "Register New Person",
            "Add someone new by capturing their face",
            accent="#10B981",
        )

        actions = QHBoxLayout()
        actions.setSpacing(14)
        actions.addWidget(self.attendance_card, 1)
        actions.addWidget(self.register_card, 1)

        self.attendance_card.clicked.connect(lambda: self.navigate(1))
        self.register_card.clicked.connect(lambda: self.navigate(2))

        trend_title = QLabel("Attendance — last 7 days")
        trend_title.setObjectName("panelTitle")

        self.trend_view = self.build_trend_chart()

        panel_title = QLabel("Today's attendance")
        panel_title.setObjectName("panelTitle")

        self.dash_class_combo = QComboBox()
        self.dash_class_combo.setFixedWidth(170)
        self.dash_class_combo.currentIndexChanged.connect(self.refresh_dashboard)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("ghost")

        panel_header = QHBoxLayout()
        panel_header.addWidget(panel_title)
        panel_header.addStretch()
        panel_header.addWidget(self.dash_class_combo)
        panel_header.addWidget(self.refresh_btn)

        self.recent_table = QTableWidget(0, 2)
        self.recent_table.setHorizontalHeaderLabels(["Name", "Time"])
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.setShowGrid(False)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setMinimumHeight(140)

        self.recent_empty = EmptyState(
            "No attendance yet today",
            "Open Take Attendance and scan a face to begin logging.",
        )

        self.refresh_btn.clicked.connect(self.refresh_dashboard)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 22, 30, 26)
        layout.setSpacing(16)
        layout.addWidget(header)
        layout.addLayout(stats)
        layout.addLayout(actions)
        layout.addWidget(trend_title)
        layout.addWidget(self.trend_view)
        layout.addWidget(panel_title)
        layout.addWidget(self.recent_table)
        layout.addWidget(self.recent_empty)
        return page

    def build_trend_chart(self):
        chart = QChart()
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)

        self.trend_set = QBarSet("Present")
        self.trend_set.setColor(QColor("#8B5CF6"))
        self.trend_set.setBorderColor(QColor("#8B5CF6"))

        series = QBarSeries()
        series.append(self.trend_set)
        series.setBarWidth(0.55)
        chart.addSeries(series)

        self.trend_categories = QBarCategoryAxis()
        self.trend_categories.setLabelsColor(QColor("#8B97B0"))
        chart.addAxis(self.trend_categories, Qt.AlignBottom)
        series.attachAxis(self.trend_categories)

        self.trend_values = QValueAxis()
        self.trend_values.setLabelFormat("%d")
        self.trend_values.setLabelsColor(QColor("#8B97B0"))
        self.trend_values.setGridLineColor(QColor("#1E2740"))
        self.trend_values.setLineVisible(False)
        chart.addAxis(self.trend_values, Qt.AlignLeft)
        series.attachAxis(self.trend_values)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setMinimumHeight(180)
        return view

    def refresh_trend(self):
        counts = database.get_counts_for_days(7)
        labels, values = [], []
        today = QDate.currentDate()
        for offset in range(6, -1, -1):
            d = today.addDays(-offset)
            key = d.toString("yyyy-MM-dd")
            labels.append(d.toString("ddd d"))
            values.append(counts.get(key, 0))
        self.trend_set.remove(0, self.trend_set.count())
        self.trend_set.append(values)
        self.trend_categories.clear()
        self.trend_categories.append(labels)
        self.trend_values.setRange(0, max(4, max(values) + 1))

    def refresh_dash_classes(self):
        self.dash_class_combo.blockSignals(True)
        current = self.dash_class_combo.currentData()
        self.dash_class_combo.clear()
        self.dash_class_combo.addItem("All classes", "all")
        for class_name in database.get_classes():
            self.dash_class_combo.addItem(class_name, class_name)
        if current is not None:
            index = self.dash_class_combo.findData(current)
            if index >= 0:
                self.dash_class_combo.setCurrentIndex(index)
        self.dash_class_combo.blockSignals(False)

    def on_page_changed(self, index):
        btn = self.nav_group.button(index)
        if btn:
            btn.setChecked(True)
        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.attendance_page.refresh_lists()
        elif index == 3:
            self.manage_page.refresh_table()
        elif index == 4:
            self.logs_page.reload()
        elif index == 5:
            self.reports_page.reload()

    def refresh_dashboard(self):
        students = database.list_students()
        roster = {name for name, _, _, _ in students}
        today = database.get_today_records()
        present_names = {name for name, _ in today}
        registered = len(roster)
        present = len(present_names & roster)
        absent = max(registered - present, 0)
        rate = min(round(present / registered * 100), 100) if registered else 0

        self.present_card.set_value(present)
        self.absent_card.set_value(absent)
        self.registered_card.set_value(registered)
        self.rate_card.set_value(f"{rate}%")

        self.refresh_dash_classes()

        class_name = self.dash_class_combo.currentData()
        if class_name and class_name != "all":
            rows = database.get_today_records_by_class(class_name)
        else:
            rows = today

        self.recent_table.setRowCount(len(rows))
        for i, (name, ts) in enumerate(rows):
            self.recent_table.setItem(i, 0, QTableWidgetItem(name))
            self.recent_table.setItem(i, 1, QTableWidgetItem(ts))

        self.recent_table.setVisible(bool(rows))
        self.recent_empty.setVisible(not rows)

        self.refresh_trend()

    def tick_all(self):
        for header in self.headers:
            header.tick()

    def closeEvent(self, event):
        for widget in (self.attendance_page, self.register_page):
            camera = getattr(widget, "camera", None)
            if camera:
                camera.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Attendly")
    app.setWindowIcon(branding.app_icon())
    app.setStyleSheet(theme.STYLE)

    selftest = "--selftest" in sys.argv
    splash = branding.SplashScreen()
    splash.center_on_screen()
    splash.show()

    def start():
        app.processEvents()
        today = datetime.now().strftime("%Y-%m-%d")
        if settings_module.last_backup() != today:
            try:
                database.backup_data()
                settings_module.set_last_backup(today)
            except OSError:
                pass
        window = MainWindow()
        window.show()
        splash.close()
        if selftest:
            import pin_dialog

            pin_dialog.PinDialog.prompt = staticmethod(lambda *a, **k: True)
            window.navigate(3)
            app.processEvents()
            print("SELFTEST OK")
            app.quit()

    QTimer.singleShot(650, start)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()