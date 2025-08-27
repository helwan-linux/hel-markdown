from PyQt5.QtWidgets import QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon
from translations import translations

# --- TableCreationDialog Class ---
class TableCreationDialog(QDialog):
    def __init__(self, parent=None, current_language="en"):
        super().__init__(parent)
        self.setWindowTitle(translations[current_language]["table_creation_title"])
        self.setWindowIcon(QIcon("icons/halwanmark.png"))

        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(1, 99)
        self.rows_spinbox.setValue(3)

        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setRange(1, 99)
        self.cols_spinbox.setValue(2)

        layout = QFormLayout()
        layout.addRow(translations[current_language]["rows_label"], self.rows_spinbox)
        layout.addRow(translations[current_language]["cols_label"], self.cols_spinbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_table_dimensions(self):
        return self.rows_spinbox.value(), self.cols_spinbox.value()

# --- FindReplaceDialog Class ---
class FindReplaceDialog(QDialog):
    def __init__(self, parent=None, current_language="en"):
        super().__init__(parent)
        self.current_dialog_language = current_language
        self.setWindowTitle(translations[self.current_dialog_language]["find_replace_title"])
        self.setWindowIcon(QIcon("icons/halwanmark.png"))

        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()

        layout = QFormLayout()
        layout.addRow(translations[self.current_dialog_language]["find_label"], self.find_input)
        layout.addRow(translations[self.current_dialog_language]["replace_label"], self.replace_input)

        find_buttons_layout = QHBoxLayout()
        self.find_next_button = QPushButton(translations[self.current_dialog_language]["find_next"])
        self.find_prev_button = QPushButton(translations[self.current_dialog_language]["find_prev"])
        find_buttons_layout.addWidget(self.find_next_button)
        find_buttons_layout.addWidget(self.find_prev_button)
        layout.addRow("", find_buttons_layout)

        replace_buttons_layout = QHBoxLayout()
        self.replace_button = QPushButton(translations[self.current_dialog_language]["replace_button"])
        self.replace_all_button = QPushButton(translations[self.current_dialog_language]["replace_all_button"])
        replace_buttons_layout.addWidget(self.replace_button)
        replace_buttons_layout.addWidget(self.replace_all_button)
        layout.addRow("", replace_buttons_layout)

        self.setLayout(layout)

    def update_language(self, new_language):
        self.current_dialog_language = new_language
        self.setWindowTitle(translations[new_language]["find_replace_title"])
        self.find_next_button.setText(translations[new_language]["find_next"])
        self.find_prev_button.setText(translations[new_language]["find_prev"])
        self.replace_button.setText(translations[new_language]["replace_button"])
        self.replace_all_button.setText(translations[new_language]["replace_all_button"])
