from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.setWindowTitle("Add Student" if student is None else "Edit Student")
        self.setMinimumWidth(400)

        name_label = QLabel("Full name")
        name_label.setObjectName("status")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Ayesha Khan")
        if student is not None:
            self.name_input.setText(student[0])
            self.name_input.setEnabled(False)
            self.name_input.setToolTip("Name is fixed once created")

        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Class (e.g. 8A)")
        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("Section")
        self.roll_input = QLineEdit()
        self.roll_input.setPlaceholderText("Roll No")

        if student is not None:
            _, class_name, section, roll_no = student
            self.class_input.setText(class_name)
            self.section_input.setText(section)
            self.roll_input.setText(roll_no)

        class_row = QHBoxLayout()
        class_row.setSpacing(10)
        class_row.addWidget(self.class_input, 2)
        class_row.addWidget(self.section_input, 1)
        class_row.addWidget(self.roll_input, 1)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primary")
        self.cancel_btn = QPushButton("Cancel")

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.save_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(10)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addLayout(class_row)
        layout.addLayout(buttons)

        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(self.reject)
        self.name_input.setFocus()

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Name required", "Please enter the student's name.")
            return
        self.accept()

    def values(self):
        return (
            self.name_input.text().strip(),
            self.class_input.text().strip(),
            self.section_input.text().strip(),
            self.roll_input.text().strip(),
        )