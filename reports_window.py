import csv
import html
from datetime import datetime

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QComboBox,
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


class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.headers = []
        self.title = ""

        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(180)
        self.type_combo.addItem("Daily report", "daily")
        self.type_combo.addItem("Absent list", "absent")
        self.type_combo.addItem("Monthly summary", "monthly")

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dddd, d MMMM yyyy")
        self.date_edit.setFixedHeight(42)

        self.class_combo = QComboBox()
        self.class_combo.setFixedWidth(180)

        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setObjectName("primary")

        self.summary = QLabel("")
        self.summary.setObjectName("panelTitle")

        self.table = QTableWidget(0, 0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.setObjectName("ghost")
        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.setObjectName("ghost")

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.export_csv_btn)
        actions.addWidget(self.export_pdf_btn)
        actions.addStretch()

        controls = QHBoxLayout()
        controls.setSpacing(12)
        controls.addWidget(self.type_combo)
        controls.addWidget(self.date_edit)
        controls.addWidget(self.class_combo)
        controls.addWidget(self.generate_btn)
        controls.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addLayout(controls)
        layout.addWidget(self.summary)
        layout.addWidget(self.table, 1)
        layout.addLayout(actions)

        self.generate_btn.clicked.connect(self.generate)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        self.reload()
        self.generate()

    def reload(self):
        current = self.class_combo.currentData()
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        self.class_combo.addItem("All classes", "all")
        for class_name in database.get_classes():
            self.class_combo.addItem(class_name, class_name)
        if current is not None:
            index = self.class_combo.findData(current)
            if index >= 0:
                self.class_combo.setCurrentIndex(index)
        self.class_combo.blockSignals(False)

    def _class(self):
        class_name = self.class_combo.currentData()
        return None if class_name == "all" else class_name

    def generate(self):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        class_name = self._class()
        report_type = self.type_combo.currentData()

        if report_type == "daily":
            self.headers = ["Name", "Class", "Section", "Roll No", "Status"]
            self.rows = database.get_daily_report(date_str, class_name)
            present = sum(1 for r in self.rows if r[4] == "Present")
            absent = len(self.rows) - present
            self.title = f"Daily attendance report — {date_str}"
            self.summary.setText(
                f"{date_str} — {present} present, {absent} absent, "
                f"{len(self.rows)} students"
            )
        elif report_type == "absent":
            self.headers = ["Name", "Class", "Section", "Roll No"]
            self.rows = [
                r[:4]
                for r in database.get_daily_report(date_str, class_name)
                if r[4] == "Absent"
            ]
            self.title = f"Absent list — {date_str}"
            self.summary.setText(f"{date_str} — {len(self.rows)} student(s) absent")
        else:
            year_month = date_str[:7]
            self.headers = ["Name", "Class", "Roll No", "Present Days"]
            self.rows = database.get_monthly_summary(year_month, class_name)
            self.title = f"Monthly summary — {year_month}"
            self.summary.setText(
                f"{year_month} — {len(self.rows)} student(s), "
                f"{sum(r[3] for r in self.rows)} total marks"
            )

        self.table.clear()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def export_csv(self):
        if not self.rows:
            QMessageBox.information(self, "Nothing to export", "Generate a report first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export report", "report.csv", "CSV files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)
            writer.writerows(self.rows)
        QMessageBox.information(
            self, "Exported", f"Saved {len(self.rows)} rows to\n{path}"
        )

    def export_pdf(self):
        if not self.rows:
            QMessageBox.information(self, "Nothing to export", "Generate a report first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "report.pdf", "PDF files (*.pdf)"
        )
        if not path:
            return

        rows_html = "".join(
            "<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>"
            for row in self.rows
        )
        header_html = "".join(f"<th>{html.escape(str(h))}</th>" for h in self.headers)
        document = QTextDocument()
        document.setHtml(
            "<h1 style='color:#6D5EFC;'>FaceTrack — Attendance</h1>"
            f"<h2 style='font-size:14px;'>{html.escape(self.title)}</h2>"
            f"<p style='color:#666;'>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"
            f"<table border='1' cellspacing='0' cellpadding='6'>"
            f"<tr>{header_html}</tr>{rows_html}</table>"
        )

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageSize(QPrinter.A4)
        document.print_(printer)
        QMessageBox.information(
            self, "Exported", f"PDF saved to\n{path}"
        )