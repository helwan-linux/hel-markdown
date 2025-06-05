#!/usr/bin/env python3
import sys
from PyQt5.QtGui import QFont, QIcon, QTextCursor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QSplitter, QFileDialog, QAction, QMainWindow, QMessageBox,
    QToolBar, QMenu, QShortcut, QDialog, QFormLayout, QSpinBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import markdown
from translations import translations # تأكد أن ملف translations.py موجود في نفس الدليل

# --- TableCreationDialog Class ---
# هذا الفصل يمثل النافذة المنبثقة لإنشاء الجدول
class TableCreationDialog(QDialog):
    def __init__(self, parent=None, current_language="en"):
        super().__init__(parent)
        self.setWindowTitle(translations[current_language]["create_table_title"])
        self.setWindowIcon(QIcon("icons/halwanmark.png")) # تأكد من وجود الأيقونة هنا

        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(1, 99)
        self.rows_spinbox.setValue(3) # قيمة افتراضية للصفوف

        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setRange(1, 99)
        self.cols_spinbox.setValue(2) # قيمة افتراضية للأعمدة

        layout = QFormLayout()
        layout.addRow(translations[current_language]["rows_label"], self.rows_spinbox)
        layout.addRow(translations[current_language]["cols_label"], self.cols_spinbox)

        # إضافة أزرار موافق وإلغاء
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_table_dimensions(self):
        # ترجع عدد الصفوف والأعمدة التي اختارها المستخدم
        return self.rows_spinbox.value(), self.cols_spinbox.value()

# --- MarkdownEditor Class ---
class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # اللغة الافتراضية
        self.current_language = "en"

        self.setWindowIcon(QIcon("icons/halwanmark.png"))
        self.init_ui()

    def init_ui(self):
        # محرر النصوص
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier", 12))
        self.editor.textChanged.connect(self.update_preview)

        # عرض المعاينة
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Arial", 12))

        # تقسيم النافذتين جنب بعض
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([450, 450])

        # إضافة التوزيع في الواجهة الرئيسية
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # إنشاء شريط أدوات
        self.create_toolbar()

        # متغير لحفظ مسار الملف المفتوح
        self.current_file = None

        # وضع السمات الافتراضية (فاتح)
        self.light_theme()

        # تعيين عنوان النافذة
        self.setWindowTitle(translations[self.current_language]["app_title"])

        # إنشاء status bar
        self.statusBar()

        # إضافة اختصارات لوحة المفاتيح لأكثر الوظائف استخدامًا
        self.create_shortcuts()

    def create_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_file)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.save_file_as)
        QShortcut(QKeySequence("Ctrl+Z"), self.editor, self.editor.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self.editor, self.editor.redo)
        QShortcut(QKeySequence("Ctrl+B"), self, lambda: self.insert_wrapped_text("**", "**"))
        QShortcut(QKeySequence("Ctrl+I"), self, lambda: self.insert_wrapped_text("*", "*"))
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.insert_text_at_cursor("[Link Text](http://)"))
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, lambda: self.insert_text_at_cursor("![Alt Text](url)"))
        QShortcut(QKeySequence("Ctrl+`"), self, lambda: self.insert_wrapped_text("`", "`"))
        QShortcut(QKeySequence("Ctrl+Shift+`"), self, lambda: self.insert_text_at_cursor("```\n\n```"))
        # إضافة اختصار لإنشاء الجدول (اختياري)
        QShortcut(QKeySequence("Ctrl+T"), self, self.insert_table_dialog)


    def create_toolbar(self):
        if not hasattr(self, 'toolbar'):
            self.toolbar = QToolBar("Tools")
            self.addToolBar(self.toolbar)
        else:
            self.toolbar.clear()

        # زر جديد
        new_action = QAction(translations[self.current_language]["new"], self)
        new_action.triggered.connect(self.new_file)
        self.toolbar.addAction(new_action)

        # زر فتح
        open_action = QAction(translations[self.current_language]["open"], self)
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)

        # زر حفظ
        save_action = QAction(translations[self.current_language]["save"], self)
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)

        # زر حفظ باسم
        save_as_action = QAction(translations[self.current_language]["save_as"], self)
        save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(save_as_action)

        self.toolbar.addSeparator()

        # Undo
        undo_action = QAction(translations[self.current_language]["undo"], self)
        undo_action.triggered.connect(self.editor.undo)
        self.toolbar.addAction(undo_action)

        # Redo
        redo_action = QAction(translations[self.current_language]["redo"], self)
        redo_action.triggered.connect(self.editor.redo)
        self.toolbar.addAction(redo_action)

        self.toolbar.addSeparator()

        # قائمة تنسيق Markdown
        format_menu = QMenu(translations[self.current_language]["format"], self)
        format_menu.addAction(translations[self.current_language]["heading1"], self.insert_heading1)
        format_menu.addAction(translations[self.current_language]["heading2"], self.insert_heading2)
        format_menu.addAction(translations[self.current_language]["heading3"], lambda: self.insert_text_at_cursor("### "))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["bold"], lambda: self.insert_wrapped_text("**", "**"))
        format_menu.addAction(translations[self.current_language]["italic"], lambda: self.insert_wrapped_text("*", "*"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["bullet_list"], lambda: self.insert_text_at_cursor("- "))
        format_menu.addAction(translations[self.current_language]["numbered_list"], lambda: self.insert_text_at_cursor("1. "))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["link"], lambda: self.insert_text_at_cursor("[Link Text](http://)"))
        format_menu.addAction(translations[self.current_language]["image"], lambda: self.insert_text_at_cursor("![Alt Text](url)"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["inline_code"], lambda: self.insert_wrapped_text("`", "`"))
        format_menu.addAction(translations[self.current_language]["code_block"], lambda: self.insert_text_at_cursor("```\n\n```"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["blockquote"], lambda: self.insert_text_at_cursor("> "))
        format_menu.addAction(translations[self.current_language]["horizontal_line"], lambda: self.insert_text_at_cursor("\n---\n"))
        format_menu.addSeparator()
        # هنا التعديل: استدعاء الدالة الجديدة لإنشاء الجدول
        format_menu.addAction(translations[self.current_language]["table"], self.insert_table_dialog)

        format_action = QAction(translations[self.current_language]["format"], self)
        format_action.setMenu(format_menu)
        self.toolbar.addAction(format_action)

        self.toolbar.addSeparator()

        # تبديل السمة
        toggle_theme_action = QAction(translations[self.current_language]["toggle_theme"], self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(toggle_theme_action)

        # مساعدة
        help_action = QAction(translations[self.current_language]["help"], self)
        help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(help_action)

        self.toolbar.addSeparator()

        # قائمة اختيار اللغة (دائما نعيد إضافتها بالتحديث الصحيح)
        language_menu = QMenu(translations[self.current_language]["language"], self)
        en_action = QAction("English", self)
        ar_action = QAction("العربية", self)
        language_menu.addAction(en_action)
        language_menu.addAction(ar_action)

        en_action.triggered.connect(lambda: self.change_language("en"))
        ar_action.triggered.connect(lambda: self.change_language("ar"))

        language_action = QAction(translations[self.current_language]["language"], self)
        language_action.setMenu(language_menu)
        self.toolbar.addAction(language_action)

    def insert_text_at_cursor(self, text):
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def insert_wrapped_text(self, prefix, suffix):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        if selected:
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(suffix))
            self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def insert_heading1(self):
        self.insert_text_at_cursor("# ")

    def insert_heading2(self):
        self.insert_text_at_cursor("## ")

    # --- الدوال الجديدة لإدراج الجدول ---
    def insert_table_dialog(self):
        # إنشاء واستعراض نافذة الحوار لإنشاء الجدول
        dialog = TableCreationDialog(self, self.current_language)
        if dialog.exec_() == QDialog.Accepted: # إذا ضغط المستخدم على "موافق"
            rows, cols = dialog.get_table_dimensions() # احصل على الأبعاد من النافذة
            markdown_table = self.generate_markdown_table(rows, cols) # أنشئ نص الماركداون
            self.insert_text_at_cursor(markdown_table) # أدرج الجدول في المحرر
            self.statusBar().showMessage(translations[self.current_language]["table_inserted"].format(rows, cols))

    def generate_markdown_table(self, rows, cols):
        if rows <= 0 or cols <= 0:
            return ""

        # صف الرأس (Header row)
        # مثال: | Header 1 | Header 2 |
        header_row = "| " + " | ".join([f"Header {i+1}" for i in range(cols)]) + " |\n"

        # صف الفاصل (Separator row)
        # مثال: |----------|----------|
        # نستخدم 10 شرطات كافتراضي، يمكن زيادتها
        separator_row = "| " + " | ".join(["-" * 10 for _ in range(cols)]) + " |\n"

        # صفوف البيانات (Data rows)
        data_rows = []
        for r in range(rows):
            # مثال: | Cell 1,1 | Cell 1,2 |
            row_content = "| " + " | ".join([f"Cell {r+1},{c+1}" for c in range(cols)]) + " |"
            data_rows.append(row_content)

        # دمج جميع الأجزاء لإنشاء الجدول الكامل
        return header_row + separator_row + "\n".join(data_rows) + "\n"
    # --- نهاية الدوال الجديدة ---


    def update_preview(self):
        raw_text = self.editor.toPlainText()
        # إضافة دعم جداول وفك الرموز الخاصة (extensions)
        html = markdown.markdown(raw_text, extensions=['fenced_code', 'tables', 'codehilite', 'toc'])

        # تحديد الألوان بناءً على الثيم الحالي لتطبيقها في CSS
        if self.styleSheet(): # إذا كان هناك ستايل شيت، نفترض أنه الثيم الداكن
            text_color = "#f0f0f0"
            border_color = "#555"
            header_bg = "#444"
            code_bg = "#3a3a3a" # خلفية أفتح قليلاً للكود في الوضع الداكن
        else: # الثيم الفاتح
            text_color = "#000000"
            border_color = "#ddd"
            header_bg = "#f2f2f2"
            code_bg = "#eaeaea" # خلفية أغمق قليلاً للكود في الوضع الفاتح

        # حقن تنسيقات CSS لضمان عرض أفضل للجداول ومقاطع الكود
        css_style = f"""
        <style>
            body {{
                color: {text_color}; /* التأكد من أن لون النص يتطابق مع الثيم */
            }}
            table {{
                border-collapse: collapse; /* دمج حدود الخلايا لتبدو كخط واحد */
                width: 100%; /* جعل الجدول يملأ العرض المتاح */
                margin-top: 10px; /* مسافة أعلى الجدول */
                margin-bottom: 10px; /* مسافة أسفل الجدول */
            }}
            th, td {{
                border: 1px solid {border_color}; /* حدود الخلايا */
                padding: 8px; /* مسافة داخلية للخلايا */
                text-align: left; /* محاذاة النص لليسار */
            }}
            th {{
                background-color: {header_bg}; /* خلفية رؤوس الجداول */
                font-weight: bold; /* نص سميك لرؤوس الجداول */
            }}
            /* تنسيق مقاطع الكود */
            pre {{
                background-color: {code_bg};
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto; /* السماح بالتمرير الأفقي لأسطر الكود الطويلة */
            }}
            code {{
                font-family: 'Courier New', Courier, monospace; /* خط monospace للكود */
            }}
        </style>
        """
        self.preview.setHtml(css_style + html)

    def new_file(self):
        self.editor.clear()
        self.current_file = None
        self.statusBar().showMessage(translations[self.current_language]["file_new_message"])
        self.update_window_title()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, translations[self.current_language]["open"], "",
                                              "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
                self.current_file = path
                self.statusBar().showMessage(translations[self.current_language]["file_opened"].format(path))
                self.update_window_title()
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_open"].format(str(e)))

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.statusBar().showMessage(translations[self.current_language]["file_saved"].format(self.current_file))
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_save"].format(str(e)))
        else:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, translations[self.current_language]["save_as"], "",
                                              "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.current_file = path
                self.statusBar().showMessage(translations[self.current_language]["file_saved"].format(path))
                self.update_window_title()
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_save"].format(str(e)))

    def update_window_title(self):
        title = translations[self.current_language]["app_title"]
        if self.current_file:
            title += f" - {self.current_file}"
        self.setWindowTitle(title)

    def toggle_theme(self):
        # يغير الثيم من فاتح إلى داكن والعكس
        if self.styleSheet(): # إذا كان هناك ستايل شيت (نفترض أنه داكن)
            self.light_theme()
        else:
            self.dark_theme()
        # أعد تحديث المعاينة بعد تغيير الثيم لتطبيق ألوان CSS الصحيحة
        self.update_preview()

    def light_theme(self):
        self.setStyleSheet("") # إزالة أي ستايل شيت مطبق (يعود للوضع الافتراضي/الفاتح)
        self.statusBar().showMessage(translations[self.current_language]["theme_light"])

    def dark_theme(self):
        dark_stylesheet = """
            QTextEdit {
                background-color: #2e2e2e;
                color: #f0f0f0;
            }
            QMainWindow {
                background-color: #232323;
            }
            QToolBar {
                background-color: #3c3c3c;
                border: none; /* إزالة الحدود لجعلها تبدو أنظف */
            }
            QToolBar QToolButton {
                color: #f0f0f0;
                background-color: #3c3c3c;
                padding: 5px;
                border-radius: 3px;
            }
            QToolBar QToolButton:hover {
                background-color: #505050;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QMenuBar::item:selected {
                background-color: #505050;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QSplitter::handle {
                background-color: #505050;
            }
        """
        self.setStyleSheet(dark_stylesheet)
        self.statusBar().showMessage(translations[self.current_language]["theme_dark"])

    def change_language(self, lang):
        if lang not in translations:
            return
        self.current_language = lang
        self.create_toolbar() # أعد إنشاء شريط الأدوات لتحديث النصوص
        self.update_window_title() # أعد تحديث عنوان النافذة
        self.statusBar().showMessage(translations[self.current_language]["language_changed"])
        # أعد تحديث المعاينة والنصوص الأخرى
        self.editor.setPlaceholderText(translations[self.current_language].get("editor_placeholder", "")) # إذا كان هناك placeholder
        self.update_preview() # تحديث ألوان المعاينة إذا كانت تعتمد على الثيم واللغة

    def show_help(self):
        help_text = translations[self.current_language]["help_text"]
        QMessageBox.information(self, translations[self.current_language]["help"], help_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())
