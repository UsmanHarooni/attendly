import csv

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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
import face_trainer
from student_dialog import StudentDialog
from widgets import EmptyState


class ManageWindow(QWidget):
    people_updated = Signal(str)

    def __init__(self, parent=None, embedded=False):
        super().__init__(parent)
        self.embedded = embedded

        subtitle = QLabel(
            "The roster drives attendance, reports and manual marking. "
            "Faces only need to be registered for camera scanning."
        )
        subtitle.setObjectName("status")
        subtitle.setWordWrap(True)

        self.add_btn = QPushButton("Add Student")
        self.add_btn.setObjectName("primary")
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.setObjectName("ghost")
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setObjectName("ghost")
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("danger")
        self.retrain_btn = QPushButton("Retrain Model")
        self.retrain_btn.setObjectName("ghost")
        self.export_btn = QPushButton("Export Roster")
        self.export_btn.setObjectName("ghost")

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addWidget(self.retrain_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addStretch()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Class", "Section", "Roll No", "Photos"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for col in (2, 3, 4):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        self.empty = EmptyState(
            "No students yet",
            "Add a student, or import a CSV roster. Then register their faces "
            "to enable camera scanning.",
            icon="✚",
        )

        self.refresh_table()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(subtitle)
        layout.addLayout(toolbar)
        layout.addWidget(self.table)
        layout.addWidget(self.empty)

        self.add_btn.clicked.connect(self.add_student)
        self.import_btn.clicked.connect(self.import_csv)
        self.edit_btn.clicked.connect(self.edit_student)
        self.delete_btn.clicked.connect(self.delete_student)
        self.retrain_btn.clicked.connect(self.retrain)
        self.export_btn.clicked.connect(self.export_roster)

    def refresh_list(self):
        self.refresh_table()

    def refresh_table(self):
        students = database.list_students()
        self.table.setRowCount(len(students))
        for i, (name, class_name, section, roll_no) in enumerate(students):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(class_name))
            self.table.setItem(i, 2, QTableWidgetItem(section))
            self.table.setItem(i, 3, QTableWidgetItem(roll_no))
            self.table.setItem(
                i, 4, QTableWidgetItem(str(face_trainer.count_photos(name)))
            )
        self.table.setVisible(bool(students))
        self.empty.setVisible(not students)

    def add_student(self):
        dialog = StudentDialog(self)
        if dialog.exec() != StudentDialog.Accepted:
            return
        name, class_name, section, roll_no = dialog.values()
        if database.add_student(name, class_name, section, roll_no):
            self.refresh_table()
            self.people_updated.emit(f"{name} added to the roster")
        else:
            QMessageBox.warning(self, "Already exists", f"{name} is already in the roster.")

    def edit_student(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Nothing selected", "Select a student to edit.")
            return
        name = self.table.item(row, 0).text()
        student = database.get_student(name)
        if student is None:
            return
        dialog = StudentDialog(self, student=student)
        if dialog.exec() != StudentDialog.Accepted:
            return
        _, class_name, section, roll_no = dialog.values()
        database.update_student(name, class_name, section, roll_no)
        self.refresh_table()
        self.people_updated.emit(f"{name} updated")

    def delete_student(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Nothing selected", "Select a student to delete.")
            return
        name = self.table.item(row, 0).text()
        answer = QMessageBox.question(
            self,
            "Delete student",
            f"Delete {name} from the roster and remove their face photos?\n"
            "Attendance history is kept for records.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        database.delete_student(name)
        face_trainer.delete_person(name)
        self.refresh_table()
        self.people_updated.emit(f"{name} was removed")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import roster", "", "CSV files (*.csv)"
        )
        if not path:
            return
        rows = self._parse_csv(path)
        if not rows:
            QMessageBox.warning(
                self,
                "Nothing to import",
                "No valid rows found. Expected columns: Name, Class, Section, Roll.",
            )
            return
        added, skipped = database.import_students(rows)
        self.refresh_table()
        self.people_updated.emit(
            f"Imported {added} students" + (f", {skipped} skipped" if skipped else "")
        )

    def _parse_csv(self, path):
        rows = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            first = next(reader, None)
            if first is None:
                return rows
            header = {h.strip().lower(): i for i, h in enumerate(first)}
            if header and "name" in header:
                idx_name = header["name"]
                idx_class = header.get("class", header.get("class_name", 1))
                idx_section = header.get("section", 2)
                idx_roll = header.get("roll", header.get("roll no", 3))
                for line in reader:
                    if not line or not line[idx_name].strip():
                        continue
                    def pick(i):
                        return line[i].strip() if i < len(line) else ""
                    rows.append((line[idx_name].strip(), pick(idx_class), pick(idx_section), pick(idx_roll)))
            else:
                rows.append((first[0].strip(), first[1].strip() if len(first) > 1 else "", first[2].strip() if len(first) > 2 else "", first[3].strip() if len(first) > 3 else ""))
                for line in reader:
                    if not line or not line[0].strip():
                        continue
                    rows.append((line[0].strip(), line[1].strip() if len(line) > 1 else "", line[2].strip() if len(line) > 2 else "", line[3].strip() if len(line) > 3 else ""))
        return rows

    def export_roster(self):
        students = database.list_students()
        if not students:
            QMessageBox.information(self, "Nothing to export", "The roster is empty.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export roster", "roster.csv", "CSV files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Class", "Section", "Roll No", "Photos"])
            for name, class_name, section, roll_no in students:
                writer.writerow(
                    [name, class_name, section, roll_no, face_trainer.count_photos(name)]
                )
        self.people_updated.emit(f"Roster exported ({len(students)} students)")

    def retrain(self):
        if face_trainer.train_model():
            self.people_updated.emit("Model retrained")
        else:
            QMessageBox.warning(self, "Nothing to train", "No face photos found.")