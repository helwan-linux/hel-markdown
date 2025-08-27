from PyQt5.QtWidgets import QMessageBox
from translations import translations
import markdown

class ThemeManager:
    def __init__(self, parent):
        self.parent = parent
        self.is_dark_theme = False

    def toggle_theme(self):
        if self.is_dark_theme:
            self.light_theme()
        else:
            self.dark_theme()
        
        for i in range(self.parent.tab_widget.count()):
            container_widget = self.parent.tab_widget.widget(i)
            if hasattr(container_widget, 'editor') and hasattr(container_widget, 'preview'):
                self.update_single_tab_preview(container_widget.editor, container_widget.preview)

    def light_theme(self):
        self.parent.setStyleSheet("")
        self.is_dark_theme = False
        self.parent.statusBar_message.showMessage(translations[self.parent.current_language]["light_theme"])

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
        self.parent.setStyleSheet(dark_stylesheet)
        self.is_dark_theme = True
        self.parent.statusBar_message.showMessage(translations[self.parent.current_language]["dark_theme"])
    
    def update_single_tab_preview(self, editor, preview):
        raw_text = editor.toPlainText()
        html = markdown.markdown(raw_text, extensions=['fenced_code', 'tables', 'codehilite', 'toc'])
        
        if self.is_dark_theme:
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
            body {{ color: {text_color}; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 10px; }}
            th, td {{ border: 1px solid {border_color}; padding: 8px; text-align: left; }}
            th {{ background-color: {header_bg}; font-weight: bold; }}
            pre {{ background-color: {code_bg}; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            code {{ font-family: 'Courier New', Courier, monospace; }}
        </style>
        """
        preview.setHtml(css_style + html)
