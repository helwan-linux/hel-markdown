from PyQt5.QtGui import QTextCursor, QClipboard
from PyQt5.QtWidgets import QApplication

class FormatActions:
    def __init__(self, main_window):
        self.main_window = main_window

    def get_editor_and_cursor(self):
        editor = self.main_window.get_current_editor()
        if not editor:
            return None, None
        return editor, editor.textCursor()

    def insert_text_at_cursor(self, text):
        editor, cursor = self.get_editor_and_cursor()
        if editor:
            cursor.insertText(text)
            self.main_window.statusBar().showMessage(f"Inserted: {text}")

    def insert_wrapped_text(self, before, after):
        editor, cursor = self.get_editor_and_cursor()
        if not editor: return

        selected_text = cursor.selectedText()
        if selected_text:
            cursor.insertText(before + selected_text + after)
        else:
            cursor.insertText(before + after)
        self.main_window.statusBar().showMessage(f"Wrapped text with: {before} and {after}")

    def undo(self):
        editor = self.main_window.get_current_editor()
        if editor:
            editor.undo()
            self.main_window.statusBar().showMessage("Undo successful.")

    def redo(self):
        editor = self.main_window.get_current_editor()
        if editor:
            editor.redo()
            self.main_window.statusBar().showMessage("Redo successful.")
            
    def convert_case(self, case_type):
        editor, cursor = self.get_editor_and_cursor()
        if not editor:
            return

        selected_text = cursor.selectedText()
        if not selected_text:
            return

        if case_type == "upper":
            new_text = selected_text.upper()
        elif case_type == "lower":
            new_text = selected_text.lower()
        else:
            return

        cursor.insertText(new_text)
