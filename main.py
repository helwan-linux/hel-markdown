#!/usr/bin/env python3
import sys
import os

from PyQt5.QtGui import QFont, QIcon, QTextCursor, QTextDocument
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QSplitter, QFileDialog, QAction, QMainWindow, QMessageBox,
    QToolBar, QMenu, QShortcut, QDialog, QFormLayout, QSpinBox,
    QDialogButtonBox, QHBoxLayout, QLineEdit, QPushButton, QTabWidget,
    QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

import markdown
from translations import translations

# --- TableCreationDialog Class ---
class TableCreationDialog(QDialog):
    def __init__(self, parent=None, current_language="en"):
        super().__init__(parent)
        self.setWindowTitle(translations[current_language]["create_table_title"])
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
# --- FindReplaceDialog Class ---
class FindReplaceDialog(QDialog):
    def __init__(self, parent=None, current_language="en"):
        super().__init__(parent)
        # تخزين اللغة كخاصية يمكن الوصول إليها لتحديثات لاحقة
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
        # لا تحتاج لتغيير نص input field placeholders إذا كانت غير موجودة أو لم تستخدم
        # self.find_input.setPlaceholderText(translations[new_language]["find_label"])
        # self.replace_input.setPlaceholderText(translations[new_language]["replace_label"])
        self.find_next_button.setText(translations[new_language]["find_next"])
        self.find_prev_button.setText(translations[new_language]["find_prev"])
        self.replace_button.setText(translations[new_language]["replace_button"])
        self.replace_all_button.setText(translations[new_language]["replace_all_button"])

# --- MarkdownEditor Class ---
class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_language = "en"
        self.setWindowIcon(QIcon("icons/halwanmark.png"))
        self.find_replace_dialog = None

        self.init_ui()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tab_widget)

        self.statusBar_message = self.statusBar()
        self.word_count_label = self.statusBar_message.addPermanentWidget(QLabel(""))
        self.char_count_label = self.statusBar_message.addPermanentWidget(QLabel(""))

        self.tab_widget.currentChanged.connect(self.update_status_bar_for_current_tab)

        self.create_toolbar()
        self.light_theme()

        self.setWindowTitle(translations[self.current_language]["app_title"])
        self.create_shortcuts()

        self.new_file() # هذا سيستدعي update_preview_and_counts التي ستحدث العدادات


    # --- إدارة التبويبات (Tabs) ---
    def add_new_tab(self, editor_text="", file_path=None):
        container_widget = QWidget()
        main_layout = QVBoxLayout(container_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        editor = QTextEdit()
        editor.setFont(QFont("Courier", 12))
        # ربط إشارة textChanged بـ update_preview_and_counts و set_tab_modified
        editor.textChanged.connect(self.update_preview_and_counts)
        # هنا سنمرر container_widget للـ lambda حتى تتمكن set_tab_modified من الوصول إليه
        editor.textChanged.connect(lambda editor=editor: self.set_tab_modified_by_editor(editor, True))


        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setFont(QFont("Arial", 12))

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(editor)
        splitter.addWidget(preview)
        splitter.setSizes([450, 450])

        main_layout.addWidget(splitter)

        # تخزين البيانات كخصائص مباشرة على الـ container_widget
        container_widget.editor = editor
        container_widget.preview = preview
        container_widget.current_file = file_path
        container_widget.is_modified = False # افتراضيًا غير معدّل

        tab_title = translations[self.current_language]["untitled_file"]
        if file_path:
            tab_title = os.path.basename(file_path)
        
        editor.setPlainText(editor_text)

        tab_index = self.tab_widget.addTab(container_widget, tab_title)
        self.tab_widget.setCurrentIndex(tab_index)
        self.set_tab_modified_by_editor(editor, False) # افتراضيًا غير معدّل عند الفتح أو الجديد

        # تحديث المعاينة الأولية
        self.update_preview_and_counts()


    def get_current_container_widget(self):
        # هذه الدالة ترجع الـ QWidget الذي يحتوي على المحرر والمعاينة
        return self.tab_widget.currentWidget()

    def get_current_editor(self):
        container = self.get_current_container_widget()
        return container.editor if container and hasattr(container, 'editor') else None

    def get_current_preview(self):
        container = self.get_current_container_widget()
        return container.preview if container and hasattr(container, 'preview') else None

    def get_current_file(self):
        container = self.get_current_container_widget()
        return container.current_file if container and hasattr(container, 'current_file') else None

    def set_current_file(self, file_path):
        container = self.get_current_container_widget()
        if container:
            container.current_file = file_path
            tab_index = self.tab_widget.indexOf(container) # الحصول على الفهرس من الكائن
            tab_title = os.path.basename(file_path) if file_path else translations[self.current_language]["untitled_file"]
            self.tab_widget.setTabText(tab_index, tab_title)
            self.set_tab_modified_by_editor(container.editor, False) # حفظ يعني غير معدّل

    def set_tab_modified_by_editor(self, editor_widget, modified):
        # البحث عن الـ container_widget الذي يحتوي على هذا الـ editor_widget
        for i in range(self.tab_widget.count()):
            container_widget = self.tab_widget.widget(i)
            if hasattr(container_widget, 'editor') and container_widget.editor is editor_widget:
                container_widget.is_modified = modified
                title = self.tab_widget.tabText(i)
                # Remove any existing asterisk first to avoid multiple
                if title.endswith("*"):
                    title = title[:-1]
                
                if modified:
                    self.tab_widget.setTabText(i, title + "*")
                else:
                    self.tab_widget.setTabText(i, title)
                return


    def close_tab(self, index):
        container_widget = self.tab_widget.widget(index)
        if hasattr(container_widget, 'is_modified') and container_widget.is_modified:
            tab_title = self.tab_widget.tabText(index)
            # إذا كانت النجمة موجودة، أزلها مؤقتًا للعرض في الرسالة
            if tab_title.endswith("*"):
                tab_title = tab_title[:-1]
            reply = QMessageBox.question(self, translations[self.current_language]["app_title"],
                                         translations[self.current_language]["save_changes_prompt"].format(tab_title),
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if reply == QMessageBox.Save:
                if not self.save_file_at_index(index): # حاول الحفظ، إذا فشل لا تغلق
                    return
            elif reply == QMessageBox.Cancel:
                return
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.new_file() # افتح تبويب جديد إذا أغلقت كل التبويبات

    def save_file_at_index(self, index):
        container_widget = self.tab_widget.widget(index)
        if not container_widget or not hasattr(container_widget, 'editor'):
            return False

        editor = container_widget.editor
        file_path = container_widget.current_file

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(editor.toPlainText())
                self.statusBar_message.showMessage(translations[self.current_language]["file_saved"].format(file_path))
                self.set_tab_modified_by_editor(editor, False)
                return True
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_save"].format(str(e)))
                return False
        else:
            path, _ = QFileDialog.getSaveFileName(self, translations[self.current_language]["save_as"], "",
                                                  "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)")
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(editor.toPlainText())
                    container_widget.current_file = path # تحديث المسار في بيانات التبويب
                    self.statusBar_message.showMessage(translations[self.current_language]["file_saved"].format(path))
                    self.set_tab_modified_by_editor(editor, False)
                    # تحديث عنوان التبويب
                    self.tab_widget.setTabText(index, os.path.basename(path))
                    return True
                except Exception as e:
                    QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_save"].format(str(e)))
                    return False
            return False # المستخدم ألغى الحفظ


    def update_status_bar_for_current_tab(self):
        current_editor = self.get_current_editor()
        if current_editor:
            self.update_counts(current_editor.toPlainText())
        else:
            self.update_counts("")

    def create_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_file)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.save_file_as)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_current_editor)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo_current_editor)
        QShortcut(QKeySequence("Ctrl+B"), self, lambda: self.insert_wrapped_text_current_editor("**", "**"))
        QShortcut(QKeySequence("Ctrl+I"), self, lambda: self.insert_wrapped_text_current_editor("*", "*"))
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.insert_text_at_cursor_current_editor("[Link Text](http://)"))
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, lambda: self.insert_text_at_cursor_current_editor("![Alt Text](url)"))
        QShortcut(QKeySequence("Ctrl+`"), self, lambda: self.insert_wrapped_text_current_editor("`", "`"))
        QShortcut(QKeySequence("Ctrl+Shift+`"), self, lambda: self.insert_text_at_cursor_current_editor("```\n\n```"))
        QShortcut(QKeySequence("Ctrl+T"), self, self.insert_table_dialog)
        QShortcut(QKeySequence("Ctrl+F"), self, self.show_find_replace_dialog)

    def undo_current_editor(self):
        editor = self.get_current_editor()
        if editor: editor.undo()

    def redo_current_editor(self):
        editor = self.get_current_editor()
        if editor: editor.redo()

    def insert_text_at_cursor_current_editor(self, text):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            cursor.insertText(text)
            editor.setTextCursor(cursor)
            editor.setFocus()

    def insert_wrapped_text_current_editor(self, prefix, suffix):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            selected = cursor.selectedText()
            if selected:
                cursor.insertText(f"{prefix}{selected}{suffix}")
            else:
                cursor.insertText(f"{prefix}{suffix}")
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(suffix))
                editor.setTextCursor(cursor)
            editor.setFocus()

    def create_toolbar(self):
        if not hasattr(self, 'toolbar'):
            self.toolbar = QToolBar("Tools")
            self.addToolBar(self.toolbar)
        else:
            self.toolbar.clear()

        new_action = QAction(translations[self.current_language]["new"], self)
        new_action.triggered.connect(self.new_file)
        self.toolbar.addAction(new_action)

        open_action = QAction(translations[self.current_language]["open"], self)
        open_action.triggered.connect(self.open_file)
        self.toolbar.addAction(open_action)

        save_action = QAction(translations[self.current_language]["save"], self)
        save_action.triggered.connect(self.save_file)
        self.toolbar.addAction(save_action)

        save_as_action = QAction(translations[self.current_language]["save_as"], self)
        save_as_action.triggered.connect(self.save_file_as)
        self.toolbar.addAction(save_as_action)

        self.toolbar.addSeparator()

        undo_action = QAction(translations[self.current_language]["undo"], self)
        undo_action.triggered.connect(self.undo_current_editor)
        self.toolbar.addAction(undo_action)

        redo_action = QAction(translations[self.current_language]["redo"], self)
        redo_action.triggered.connect(self.redo_current_editor)
        self.toolbar.addAction(redo_action)

        self.toolbar.addSeparator()

        format_menu = QMenu(translations[self.current_language]["format"], self)
        format_menu.addAction(translations[self.current_language]["heading1"], self.insert_heading1)
        format_menu.addAction(translations[self.current_language]["heading2"], self.insert_heading2)
        format_menu.addAction(translations[self.current_language]["heading3"], lambda: self.insert_text_at_cursor_current_editor("### "))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["bold"], lambda: self.insert_wrapped_text_current_editor("**", "**"))
        format_menu.addAction(translations[self.current_language]["italic"], lambda: self.insert_wrapped_text_current_editor("*", "*"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["bullet_list"], lambda: self.insert_text_at_cursor_current_editor("- "))
        format_menu.addAction(translations[self.current_language]["numbered_list"], lambda: self.insert_text_at_cursor_current_editor("1. "))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["link"], lambda: self.insert_text_at_cursor_current_editor("[Link Text](http://)"))
        format_menu.addAction(translations[self.current_language]["image"], lambda: self.insert_text_at_cursor_current_editor("![Alt Text](url)"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["inline_code"], lambda: self.insert_wrapped_text_current_editor("`", "`"))
        format_menu.addAction(translations[self.current_language]["code_block"], lambda: self.insert_text_at_cursor_current_editor("```\n\n```"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["blockquote"], lambda: self.insert_text_at_cursor_current_editor("> "))
        format_menu.addAction(translations[self.current_language]["horizontal_line"], lambda: self.insert_text_at_cursor_current_editor("\n---\n"))
        format_menu.addSeparator()
        format_menu.addAction(translations[self.current_language]["table"], self.insert_table_dialog)

        format_action = QAction(translations[self.current_language]["format"], self)
        format_action.setMenu(format_menu)
        self.toolbar.addAction(format_action)

        self.toolbar.addSeparator()

        find_replace_action = QAction(translations[self.current_language]["find_replace_title"], self)
        find_replace_action.triggered.connect(self.show_find_replace_dialog)
        self.toolbar.addAction(find_replace_action)

        self.toolbar.addSeparator()

        export_html_action = QAction(translations[self.current_language]["export_html"], self)
        export_html_action.triggered.connect(self.export_to_html)
        self.toolbar.addAction(export_html_action)

        self.toolbar.addSeparator()

        toggle_theme_action = QAction(translations[self.current_language]["toggle_theme"], self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(toggle_theme_action)

        help_action = QAction(translations[self.current_language]["help"], self)
        help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(help_action)

        self.toolbar.addSeparator()

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

    def insert_heading1(self):
        self.insert_text_at_cursor_current_editor("# ")

    def insert_heading2(self):
        self.insert_text_at_cursor_current_editor("## ")

    def insert_table_dialog(self):
        dialog = TableCreationDialog(self, self.current_language)
        if dialog.exec_() == QDialog.Accepted:
            rows, cols = dialog.get_table_dimensions()
            markdown_table = self.generate_markdown_table(rows, cols)
            self.insert_text_at_cursor_current_editor(markdown_table)
            self.statusBar_message.showMessage(translations[self.current_language]["table_inserted"].format(rows, cols))

    def generate_markdown_table(self, rows, cols):
        if rows <= 0 or cols <= 0:
            return ""

        header_row = "| " + " | ".join([f"Header {i+1}" for i in range(cols)]) + " |\n"
        separator_row = "| " + " | ".join(["-" * 10 for _ in range(cols)]) + " |\n"

        data_rows = []
        for r in range(rows):
            row_content = "| " + " | ".join([f"Cell {r+1},{c+1}" for c in range(cols)]) + " |"
            data_rows.append(row_content)

        return header_row + separator_row + "\n".join(data_rows) + "\n"

    def show_find_replace_dialog(self):
        if not self.get_current_editor():
            QMessageBox.warning(self, "Error", "No editor open.")
            return

        if not self.find_replace_dialog:
            self.find_replace_dialog = FindReplaceDialog(self, self.current_language)
            self.find_replace_dialog.find_next_button.clicked.connect(self.find_next)
            self.find_replace_dialog.find_prev_button.clicked.connect(self.find_previous)
            self.find_replace_dialog.replace_button.clicked.connect(self.replace_text)
            self.find_replace_dialog.replace_all_button.clicked.connect(self.replace_all)
            self.find_replace_dialog.setModal(False)
            self.find_replace_dialog.show()
        else:
            self.find_replace_dialog.show()
            self.find_replace_dialog.activateWindow()
        self.find_replace_dialog.find_input.setFocus()

    def find_text(self, forward=True):
        editor = self.get_current_editor()
        if not editor: return False

        find_text = self.find_replace_dialog.find_input.text()
        if not find_text: return False

        flags = QTextDocument.FindFlags()
        if not forward:
            flags |= QTextDocument.FindBackward

        cursor = editor.textCursor()
        if not cursor.hasSelection():
            if forward:
                cursor.movePosition(QTextCursor.Start)
            else:
                cursor.movePosition(QTextCursor.End)
            editor.setTextCursor(cursor)

        found = editor.find(find_text, flags)
        
        if not found:
            if forward:
                cursor.movePosition(QTextCursor.Start)
            else:
                cursor.movePosition(QTextCursor.End)
            editor.setTextCursor(cursor)
            found = editor.find(find_text, flags)
            
            if not found:
                QMessageBox.information(self, translations[self.current_language]["find_replace_title"],
                                        translations[self.current_language]["no_match_found"].format(find_text))
        return found

    def find_next(self):
        self.find_text(forward=True)

    def find_previous(self):
        self.find_text(forward=False)

    def replace_text(self):
        editor = self.get_current_editor()
        if not editor: return

        find_text = self.find_replace_dialog.find_input.text()
        replace_text = self.find_replace_dialog.replace_input.text()

        if not find_text: return

        cursor = editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == find_text:
            cursor.insertText(replace_text)
            editor.setTextCursor(cursor)
        self.find_next()

    def replace_all(self):
        editor = self.get_current_editor()
        if not editor: return

        find_text = self.find_replace_dialog.find_input.text()
        replace_text = self.find_replace_dialog.replace_input.text()

        if not find_text: return

        editor.blockSignals(True)
        doc = editor.document()
        cursor = QTextCursor(doc)
        
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

        count = 0
        while editor.find(find_text):
            current_cursor = editor.textCursor()
            if current_cursor.hasSelection():
                current_cursor.insertText(replace_text)
                count += 1
            else:
                break
        
        editor.blockSignals(False)
        self.update_preview_and_counts()
        self.statusBar_message.showMessage(f"Replaced {count} occurrences.")


    def update_counts(self, text_content):
        if text_content is None:
            text_content = ""
        words = len(text_content.split())
        chars = len(text_content)
        # تأكد من أن labels موجودة قبل محاولة setText عليها
        # هذه التحقق يضمن عدم حدوث الخطأ إذا تم استدعاء الدالة في وقت مبكر جداً
        if hasattr(self, 'word_count_label') and self.word_count_label is not None:
            self.word_count_label.setText(translations[self.current_language]["word_count"].format(words))
        if hasattr(self, 'char_count_label') and self.char_count_label is not None:
            self.char_count_label.setText(translations[self.current_language]["char_count"].format(chars))


    def update_preview_and_counts(self):
        editor = self.get_current_editor()
        preview = self.get_current_preview()
        if not editor or not preview: return

        raw_text = editor.toPlainText()
        html = markdown.markdown(raw_text, extensions=['fenced_code', 'tables', 'codehilite', 'toc'])

        if self.styleSheet():
            text_color = "#f0f0f0"
            border_color = "#555"
            header_bg = "#444"
            code_bg = "#3a3a3a"
        else:
            text_color = "#000000"
            border_color = "#ddd"
            header_bg = "#f2f2f2"
            code_bg = "#eaeaea"

        css_style = f"""
        <style>
            body {{
                color: {text_color};
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
                margin-bottom: 10px;
            }}
            th, td {{
                border: 1px solid {border_color};
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: {header_bg};
                font-weight: bold;
            }}
            pre {{
                background-color: {code_bg};
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            code {{
                font-family: 'Courier New', Courier, monospace;
            }}
        </style>
        """
        preview.setHtml(css_style + html)
        self.update_counts(raw_text)
        
        current_editor = self.get_current_editor() # احصل على المحرر الحالي للعثور على التبويب
        if current_editor:
            self.set_tab_modified_by_editor(current_editor, True)


    def new_file(self):
        self.add_new_tab()
        self.statusBar_message.showMessage(translations[self.current_language]["file_new_message"])

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, translations[self.current_language]["open"], "",
                                              "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                # ابحث إذا كان الملف مفتوحًا بالفعل في تبويب آخر
                for i in range(self.tab_widget.count()):
                    container_widget = self.tab_widget.widget(i)
                    if hasattr(container_widget, 'current_file') and container_widget.current_file == path:
                        self.tab_widget.setCurrentIndex(i) # انتقل للتبويب الموجود
                        self.statusBar_message.showMessage(translations[self.current_language]["file_opened"].format(path))
                        return

                # إذا لم يكن مفتوحًا، افتح تبويبًا جديدًا
                self.add_new_tab(editor_text=file_content, file_path=path)
                self.statusBar_message.showMessage(translations[self.current_language]["file_opened"].format(path))
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_open"].format(str(e)))

    def save_file(self):
        current_index = self.tab_widget.currentIndex()
        if current_index == -1: return
        self.save_file_at_index(current_index)
        self.update_window_title()

    def save_file_as(self):
        current_index = self.tab_widget.currentIndex()
        if current_index == -1: return

        path, _ = QFileDialog.getSaveFileName(self, translations[self.current_language]["save_as"], "",
                                              "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*)")
        if path:
            try:
                editor = self.get_current_editor()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(editor.toPlainText())
                self.set_current_file(path)
                self.statusBar_message.showMessage(translations[self.current_language]["file_saved"].format(path))
                self.update_window_title()
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["file_error_save"].format(str(e)))

    def update_window_title(self):
        base_title = translations[self.current_language]["app_title"]
        current_file = self.get_current_file()
        if current_file:
            file_name = os.path.basename(current_file)
            self.setWindowTitle(f"{base_title} - {file_name}")
        else:
            self.setWindowTitle(base_title)

    def toggle_theme(self):
        if self.styleSheet():
            self.light_theme()
        else:
            self.dark_theme()
        # بعد تغيير الثيم، نحتاج لتحديث المعاينة في جميع التبويبات لتطبيق الـ CSS الجديد
        for i in range(self.tab_widget.count()):
            container_widget = self.tab_widget.widget(i)
            if hasattr(container_widget, 'editor') and hasattr(container_widget, 'preview'):
                self._update_single_tab_preview(container_widget.editor, container_widget.preview)

    def _update_single_tab_preview(self, editor, preview):
        raw_text = editor.toPlainText()
        html = markdown.markdown(raw_text, extensions=['fenced_code', 'tables', 'codehilite', 'toc'])

        if self.styleSheet(): # Dark theme
            text_color = "#f0f0f0"
            border_color = "#555"
            header_bg = "#444"
            code_bg = "#3a3a3a"
        else: # Light theme
            text_color = "#000000"
            border_color = "#ddd"
            header_bg = "#f2f2f2"
            code_bg = "#eaeaea"

        css_style = f"""
        <style>
            body {{ color: {text_color}; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 10px; }}
            th, td {{ border: 1px solid {border_color}; padding: 8px; text-align: left; }}
            th {{ background-color: {header_bg}; font-weight: bold; }}
            pre {{ background-color: {code_bg}; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            code {{ font-family: 'Courier New', Courier, monospace; }}
        </style>
        """
        preview.setHtml(css_style + html)


    def light_theme(self):
        self.setStyleSheet("")
        self.statusBar_message.showMessage(translations[self.current_language]["theme_light"])

    def dark_theme(self):
        dark_stylesheet = """
            QTextEdit {
                background-color: #2e2e2e;
                color: #f0f0f0;
                border: 1px solid #555;
            }
            QMainWindow {
                background-color: #232323;
            }
            QToolBar {
                background-color: #3c3c3c;
                border: none;
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
            QTabWidget::pane { /* The tab widget frame */
                border-top: 1px solid #555;
            }
            QTabBar::tab {
                background: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
                border-bottom-color: #3c3c3c; /* same as pane color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 4px;
            }
            QTabBar::tab:selected {
                background: #2e2e2e; /* Editor background color */
                border-color: #555;
                border-bottom-color: #2e2e2e; /* same as pane color */
            }
            QTabBar::tab:hover {
                background: #505050;
            }
            QTabBar::tab:selected:hover {
                background: #2e2e2e;
            }
            /* Style for the close button on tabs */
            QTabBar::close-button {
                image: url(icons/close_tab_dark.png);
                subcontrol-origin: padding;
                subcontrol-position: right;
                margin-right: 2px;
            }
            QTabBar::close-button:hover {
                background: #606060;
                border-radius: 2px;
            }
        """
        self.setStyleSheet(dark_stylesheet)
        self.statusBar_message.showMessage(translations[self.current_language]["theme_dark"])

    def change_language(self, lang):
        if lang not in translations:
            return
        self.current_language = lang
        self.create_toolbar()
        self.update_window_title()
        self.statusBar_message.showMessage(translations[self.current_language]["language_changed"])
        for i in range(self.tab_widget.count()):
            container_widget = self.tab_widget.widget(i)
            if container_widget:
                tab_title = os.path.basename(container_widget.current_file) if container_widget.current_file else translations[self.current_language]["untitled_file"]
                if hasattr(container_widget, 'is_modified') and container_widget.is_modified:
                    tab_title += "*"
                self.tab_widget.setTabText(i, tab_title)
                if hasattr(container_widget, 'editor') and hasattr(container_widget, 'preview'):
                    self._update_single_tab_preview(container_widget.editor, container_widget.preview)

        # تحديث لغة مربع حوار البحث والاستبدال إذا كان موجودًا
        if self.find_replace_dialog: # لاحظ: ليس بالضرورة أن يكون isVisible()
            self.find_replace_dialog.update_language(self.current_language)

        self.update_status_bar_for_current_tab()


    def show_help(self):
        help_text = translations[self.current_language]["help_text"]
        QMessageBox.information(self, translations[self.current_language]["help"], help_text)

    def export_to_html(self):
        current_preview = self.get_current_preview()
        if not current_preview:
            QMessageBox.warning(self, "Error", "No content to export.")
            return

        current_file_path = self.get_current_file()
        suggested_name = "untitled.html"
        if current_file_path:
            base_name = os.path.splitext(os.path.basename(current_file_path))[0]
            suggested_name = f"{base_name}.html"

        path, _ = QFileDialog.getSaveFileName(self, translations[self.current_language]["export_html"],
                                              suggested_name, "HTML Files (*.html)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(current_preview.toHtml())
                self.statusBar_message.showMessage(translations[self.current_language]["html_file_saved"].format(path))
            except Exception as e:
                QMessageBox.warning(self, "Error", translations[self.current_language]["export_error"].format(str(e)))

    def closeEvent(self, event):
        for i in range(self.tab_widget.count()):
            container_widget = self.tab_widget.widget(i)
            # تأكد أن الـ container_widget ليس None قبل التحقق من الخصائص
            if container_widget and hasattr(container_widget, 'is_modified') and container_widget.is_modified:
                # نحصل على العنوان الحالي للتبويب بما فيه النجمة إن وجدت
                tab_title_with_asterisk = self.tab_widget.tabText(i)
                # لإظهار العنوان بدون النجمة في الرسالة، أزلها مؤقتاً
                display_title = tab_title_with_asterisk.replace("*", "")

                reply = QMessageBox.question(self, translations[self.current_language]["app_title"],
                                             translations[self.current_language]["save_changes_prompt"].format(display_title),
                                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                if reply == QMessageBox.Save:
                    # يجب أن نحفظ التبويب الذي تم التحقق منه حاليًا
                    # ليس بالضرورة التبويب الحالي في الواجهة (self.tab_widget.currentIndex())
                    # لذلك، نحتاج إلى دالة حفظ تعمل على تبويب معين بواسطة فهرسه
                    if not self.save_file_at_index(i): # هذه الدالة تحتاج index
                        event.ignore()
                        return
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.resize(900, 600)
    window.show()
    sys.exit(app.exec_())
