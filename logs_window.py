from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QFileDialog,
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


class LogsPage(QWidget):
    logs_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "date"
        self.rows = []

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dddd, d MMMM yyyy")
        self.date_edit.setFixedHeight(42)
        self.date_edit.dateChanged.connect(self.load_date)

        self.yesterday_btn = QPushButton("Yesterday")
        self.yesterday_btn.setObjectName("chip")
        self.yesterday_btn.setCursor(Qt.PointingHandCursor)
        self.today_btn = QPushButton("Today")
        self.today_btn.setObjectName("chip")
        self.today_btn.setCursor(Qt.PointingHandCursor)
        self.tomorrow_btn = QPushButton("Tomorrow")
        self.tomorrow_btn.setObjectName("chip")
        self.tomorrow_btn.setCursor(Qt.PointingHandCursor)
        self.all_btn = QPushButton("All records")
        self.all_btn.setObjectName("chip")
        self.all_btn.setCursor(Qt.PointingHandCursor)

        self.yesterday_btn.clicked.connect(lambda: self.jump(-1))
        self.today_btn.clicked.connect(lambda: self.jump(0))
        self.tomorrow_btn.clicked.connect(lambda: self.jump(1))
        self.all_btn.clicked.connect(self.load_all)

        chips = QHBoxLayout()
        chips.setSpacing(8)
        chips.addWidget(self.yesterday_btn)
        chips.addWidget(self.today_btn)
        chips.addWidget(self.tomorrow_btn)
        chips.addWidget(self.all_btn)
        chips.addStretch()

        date_row = QHBoxLayout()
        date_row.setSpacing(12)
        date_row.addWidget(self.date_edit)
        date_row.addLayout(chips)

        self.summary = QLabel("")
        self.summary.setObjectName("panelTitle")

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Date", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setObjectName("ghost")
        self.clear_date_btn = QPushButton("Clear This Day")
        self.clear_date_btn.setObjectName("dangerGhost")
        self.clear_all_btn = QPushButton("Clear All Logs")
        self.clear_all_btn.setObjectName("danger")

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.export_btn)
        actions.addStretch()
        actions.addWidget(self.clear_date_btn)
        actions.addWidget(self.clear_all_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addLayout(date_row)
        layout.addWidget(self.summary)
        layout.addWidget(self.table, 1)
        layout.addLayout(actions)

        self.export_btn.clicked.connect(self.export_csv)
        self.clear_date_btn.clicked.connect(self.clear_date)
        self.clear_all_btn.clicked.connect(self.clear_all)

        self.load_date()

    def jump(self, offset):
        self.date_edit.setDate(QDate.currentDate().addDays(offset))

    def reload(self):
        if self.mode == "all":
            self.load_all()
        else:
            self.load_date()

    def load_date(self):
        self.mode = "date"
        self.date_edit.setEnabled(True)
        d = self.date_edit.date().toString("yyyy-MM-dd")
        self.rows = database.get_records_for_date(d)
        self.populate()
        self.summary.setText(
            f"{len(self.rows)} record(s) for "
            f"{self.date_edit.date().toString('dddd, d MMMM yyyy')}"
        )
        self.clear_date_btn.setEnabled(bool(self.rows))

    def load_all(self):
        self.mode = "all"
        self.date_edit.setEnabled(False)
        self.rows = database.get_all_records()
        self.populate()
        self.summary.setText(f"{len(self.rows)} record(s) in total")
        self.clear_date_btn.setEnabled(False)

    def populate(self):
        self.table.setRowCount(len(self.rows))
        for i, (name, ts) in enumerate(self.rows):
            date_part, _, time_part = ts.partition(" ")
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(date_part))
            self.table.setItem(i, 2, QTableWidgetItem(time_part))

    def export_csv(self):
        if not self.rows:
            QMessageBox.information(self, "Nothing to export", "No records to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export attendance", "attendance.csv", "CSV files (*.csv)"
        )
        if not path:
            return
        database.export_records_to_csv(path, self.rows)
        QMessageBox.information(
            self, "Exported", f"Saved {len(self.rows)} records to\n{path}"
        )

    def clear_date(self):
        d = self.date_edit.date().toString("yyyy-MM-dd")
        count = len(self.rows)
        answer = QMessageBox.question(
            self,
            "Clear this day",
            f"Delete {count} attendance record(s) for {d}?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        database.clear_records_for_date(d)
        self.load_date()
        self.notify_cleared(f"Logs for {d} cleared")
        QMessageBox.information(self, "Cleared", f"Logs for {d} were deleted.")

    def clear_all(self):
        answer = QMessageBox.question(
            self,
            "Clear all logs",
            "Delete ALL attendance records?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        database.clear_all_records()
        self.date_edit.setDate(QDate.currentDate())
        self.notify_cleared("All attendance logs deleted")
        QMessageBox.information(self, "Cleared", "All attendance logs were deleted.")

    def notify_cleared(self, message):
        try:
            self.logs_changed.emit(message)
        except Exception:
            pass