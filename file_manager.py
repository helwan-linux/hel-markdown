import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from translations import translations

class FileManager:
    def __init__(self, parent):
        self.parent = parent

    def new_file(self):
        self.parent.add_new_tab()
        self.parent.statusBar_message.showMessage(translations[self.parent.current_language]["file_new_message"])

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self.parent, 
            translations[self.parent.current_language]["open"], 
            "", 
            "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*.*)"
        )
        if path:
            if self.parent.tab_widget.count() == 1 and not self.parent.get_current_editor().toPlainText() and not self.parent.get_current_file():
                self.parent.tab_widget.currentWidget().current_file = path
                self.load_file(path, self.parent.get_current_editor())
                self.parent.set_current_file(path)
            else:
                self.parent.add_new_tab(file_path=path)
                self.load_file(path, self.parent.get_current_editor())

    def load_file(self, path, editor):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            editor.setPlainText(content)
            self.parent.statusBar_message.showMessage(translations[self.parent.current_language]["file_opened"])
        except Exception as e:
            QMessageBox.critical(self.parent, translations[self.parent.current_language]["error"], f"Failed to open file: {e}")

    def save_file(self):
        current_file = self.parent.get_current_file()
        if not current_file:
            self.save_file_as()
        else:
            self.save_to_path(current_file)

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self.parent, 
            translations[self.parent.current_language]["save_as"], 
            os.path.basename(self.parent.get_current_file()) if self.parent.get_current_file() else "", 
            "Markdown files (*.md *.markdown);;Text files (*.txt);;All files (*.*)"
        )
        if path:
            self.save_to_path(path)
            self.parent.set_current_file(path)

    def save_to_path(self, path):
        editor = self.parent.get_current_editor()
        if not editor:
            return
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            self.parent.statusBar_message.showMessage(translations[self.parent.current_language]["file_saved"])
            self.parent.file_manager.set_tab_modified_by_editor(editor, False)
        except Exception as e:
            QMessageBox.critical(self.parent, translations[self.parent.current_language]["error"], f"Failed to save file: {e}")

    def set_tab_modified_by_editor(self, editor, is_modified):
        container = self.parent.tab_widget.findChild(self.parent.tab_widget.currentWidget().__class__, "container")
        
        tab_index = self.parent.tab_widget.indexOf(editor.parentWidget())
        if tab_index == -1: return

        if is_modified and not self.parent.tab_widget.tabText(tab_index).endswith("*"):
            self.parent.tab_widget.setTabText(tab_index, self.parent.tab_widget.tabText(tab_index) + "*")
            editor.parentWidget().is_modified = True
        elif not is_modified and self.parent.tab_widget.tabText(tab_index).endswith("*"):
            self.parent.tab_widget.setTabText(tab_index, self.parent.tab_widget.tabText(tab_index).rstrip('*'))
            editor.parentWidget().is_modified = False

    def close_tab(self, index):
        container = self.parent.tab_widget.widget(index)
        if container.is_modified:
            reply = QMessageBox.question(
                self.parent,
                translations[self.parent.current_language]["save_changes_title"],
                translations[self.parent.current_language]["save_changes_prompt"],
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.parent.tab_widget.setCurrentIndex(index)
                self.save_file()
                if not container.is_modified:
                    self.parent.tab_widget.removeTab(index)
            elif reply == QMessageBox.No:
                self.parent.tab_widget.removeTab(index)
        else:
            self.parent.tab_widget.removeTab(index)
        
        if self.parent.tab_widget.count() == 0:
            self.parent.new_file()
            
    def closeEvent(self, event):
        for i in range(self.parent.tab_widget.count()):
            container = self.parent.tab_widget.widget(i)
            if container.is_modified:
                self.parent.tab_widget.setCurrentIndex(i)
                display_title = os.path.basename(container.current_file) if container.current_file else translations[self.parent.current_language]["untitled_file"]
                reply = QMessageBox.question(
                    self.parent,
                    translations[self.parent.current_language]["save_changes_title"],
                    translations[self.parent.current_language]["save_changes_message"].format(display_title),
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                if reply == QMessageBox.Yes:
                    self.save_file()
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return
        event.accept()
