from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QTextDocument, QTextCursor
from dialogs import FindReplaceDialog
from translations import translations

class SearchReplace:
    def __init__(self, parent):
        self.parent = parent
        self.find_replace_dialog = None

    def show_find_replace_dialog(self):
        if not self.parent.get_current_editor():
            QMessageBox.warning(self.parent, translations[self.parent.current_language]["error"], translations[self.parent.current_language]["no_editor_open"])
            return

        if not self.find_replace_dialog:
            self.find_replace_dialog = FindReplaceDialog(self.parent, self.parent.current_language)
            self.find_replace_dialog.find_next_button.clicked.connect(self.find_next)
            self.find_replace_dialog.find_prev_button.clicked.connect(self.find_previous)
            self.find_replace_dialog.replace_button.clicked.connect(self.replace_text)
            self.find_replace_dialog.replace_all_button.clicked.connect(self.replace_all)
            self.find_replace_dialog.setModal(False)
            self.find_replace_dialog.show()
        else:
            self.find_replace_dialog.update_language(self.parent.current_language)
            self.find_replace_dialog.show()
            self.find_replace_dialog.activateWindow()
        self.find_replace_dialog.find_input.setFocus()

    def find_text(self, forward=True):
        editor = self.parent.get_current_editor()
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
                QMessageBox.information(self.parent, translations[self.parent.current_language]["find_replace_title"],
                                        translations[self.parent.current_language]["no_match_found"].format(find_text))
        return found

    def find_next(self):
        self.find_text(forward=True)

    def find_previous(self):
        self.find_text(forward=False)

    def replace_text(self):
        editor = self.parent.get_current_editor()
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
        editor = self.parent.get_current_editor()
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
        self.parent.update_preview_and_counts()
        self.parent.statusBar_message.showMessage(translations[self.parent.current_language]["replace_all_message"].format(count))
