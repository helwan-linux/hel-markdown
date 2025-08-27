import sys
import os
import re

from PyQt5.QtGui import QFont, QIcon, QTextCursor, QTextDocument, QKeySequence, QDesktopServices
from PyQt5.QtWidgets import (
	QMainWindow, QWidget, QVBoxLayout, QTextEdit, QTextBrowser,
	QSplitter, QAction, QMessageBox,
	QToolBar, QMenu, QTabWidget, QLabel, QShortcut, QFileDialog, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QUrl

import markdown
from translations import translations
from dialogs import TableCreationDialog
from utils import generate_markdown_table
from file_manager import FileManager
from format_actions import FormatActions
from theme_manager import ThemeManager
from search_replace import SearchReplace

class MarkdownEditor(QMainWindow):
	def __init__(self):
		super().__init__()

		self.current_language = "en"
		self.setWindowIcon(QIcon("icons/halwanmark.png"))
		self.find_replace_dialog = None
		self.current_theme_stylesheet = ""

		self.file_manager = FileManager(self)
		self.format_actions = FormatActions(self)
		self.theme_manager = ThemeManager(self)
		self.search_replace = SearchReplace(self)

		self.init_ui()

	def init_ui(self):
		self.tab_widget = QTabWidget()
		self.tab_widget.setTabsClosable(True)
		self.tab_widget.tabCloseRequested.connect(self.file_manager.close_tab)

		self.setCentralWidget(self.tab_widget)

		self.statusBar_message = self.statusBar()
		self.word_count_label = self.statusBar_message.addPermanentWidget(QLabel(""))
		self.char_count_label = self.statusBar_message.addPermanentWidget(QLabel(""))

		self.tab_widget.currentChanged.connect(self.update_status_bar_for_current_tab)

		self.create_toolbar()
		self.theme_manager.light_theme()

		self.setWindowTitle(translations[self.current_language]["app_title"])
		self.create_shortcuts()

		self.file_manager.new_file()
		
	def add_new_tab(self, editor_text="", file_path=None):
		container_widget = QWidget()
		main_layout = QVBoxLayout(container_widget)
		main_layout.setContentsMargins(0, 0, 0, 0)

		editor = QTextEdit()
		editor.setLayoutDirection(Qt.RightToLeft)
		editor.setFont(QFont("Courier", 12))
		editor.textChanged.connect(self.update_preview_and_counts)
		editor.textChanged.connect(lambda editor=editor: self.file_manager.set_tab_modified_by_editor(editor, True))

		preview = QTextBrowser()
		preview.setLayoutDirection(Qt.RightToLeft)
		preview.setReadOnly(True)
		preview.setFont(QFont("Arial", 12))
		preview.setOpenExternalLinks(True)
		
		splitter = QSplitter(Qt.Horizontal)
		splitter.addWidget(editor)
		splitter.addWidget(preview)
		splitter.setSizes([450, 450])

		main_layout.addWidget(splitter)

		container_widget.editor = editor
		container_widget.preview = preview
		container_widget.current_file = file_path
		container_widget.is_modified = False

		tab_title = translations[self.current_language]["untitled_file"]
		if file_path:
			tab_title = os.path.basename(file_path)
		
		editor.setPlainText(editor_text)

		tab_index = self.tab_widget.addTab(container_widget, tab_title)
		self.tab_widget.setCurrentIndex(tab_index)
		self.file_manager.set_tab_modified_by_editor(editor, False)

		self.update_preview_and_counts()

	def get_current_container_widget(self):
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
			tab_index = self.tab_widget.indexOf(container)
			tab_title = os.path.basename(file_path) if file_path else translations[self.current_language]["untitled_file"]
			self.tab_widget.setTabText(tab_index, tab_title)
			self.file_manager.set_tab_modified_by_editor(container.editor, False)

	def update_status_bar_for_current_tab(self):
		current_editor = self.get_current_editor()
		if current_editor:
			self.update_counts(current_editor.toPlainText())
		else:
			self.update_counts("")

	def create_shortcuts(self):
		QShortcut(QKeySequence("Ctrl+N"), self, self.file_manager.new_file)
		QShortcut(QKeySequence("Ctrl+O"), self, self.file_manager.open_file)
		QShortcut(QKeySequence("Ctrl+S"), self, self.file_manager.save_file)
		QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.file_manager.save_file_as)
		QShortcut(QKeySequence("Ctrl+Z"), self, self.format_actions.undo)
		QShortcut(QKeySequence("Ctrl+Y"), self, self.format_actions.redo)
		QShortcut(QKeySequence("Ctrl+B"), self, lambda: self.format_actions.insert_wrapped_text("**", "**"))
		QShortcut(QKeySequence("Ctrl+I"), self, lambda: self.format_actions.insert_wrapped_text("*", "*"))
		QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.format_actions.insert_text_at_cursor("[Link Text](http://)"))
		QShortcut(QKeySequence("Ctrl+Shift+L"), self, lambda: self.format_actions.insert_text_at_cursor("![Alt Text](url)"))
		QShortcut(QKeySequence("Ctrl+`"), self, lambda: self.format_actions.insert_wrapped_text("`", "`"))
		QShortcut(QKeySequence("Ctrl+Shift+`"), self, lambda: self.format_actions.insert_text_at_cursor("```\n\n```"))
		QShortcut(QKeySequence("Ctrl+T"), self, self.insert_table_dialog)
		QShortcut(QKeySequence("Ctrl+F"), self, self.search_replace.show_find_replace_dialog)

	def create_toolbar(self):
		if not hasattr(self, 'toolbar'):
			self.toolbar = QToolBar("Tools")
			self.addToolBar(self.toolbar)
		else:
			self.toolbar.clear()

		new_action = QAction(translations[self.current_language]["new"], self)
		new_action.triggered.connect(self.file_manager.new_file)
		self.toolbar.addAction(new_action)

		open_action = QAction(translations[self.current_language]["open"], self)
		open_action.triggered.connect(self.file_manager.open_file)
		self.toolbar.addAction(open_action)

		save_action = QAction(translations[self.current_language]["save"], self)
		save_action.triggered.connect(self.file_manager.save_file)
		self.toolbar.addAction(save_action)

		save_as_action = QAction(translations[self.current_language]["save_as"], self)
		save_as_action.triggered.connect(self.file_manager.save_file_as)
		self.toolbar.addAction(save_as_action)

		self.toolbar.addSeparator()

		undo_action = QAction(translations[self.current_language]["undo"], self)
		undo_action.triggered.connect(self.format_actions.undo)
		self.toolbar.addAction(undo_action)

		redo_action = QAction(translations[self.current_language]["redo"], self)
		redo_action.triggered.connect(self.format_actions.redo)
		self.toolbar.addAction(redo_action)

		self.toolbar.addSeparator()

		format_menu = QMenu(translations[self.current_language]["format"], self)
		format_menu.addAction(translations[self.current_language]["heading1"], lambda: self.format_actions.insert_text_at_cursor("# "))
		format_menu.addAction(translations[self.current_language]["heading2"], lambda: self.format_actions.insert_text_at_cursor("## "))
		format_menu.addAction(translations[self.current_language]["heading3"], lambda: self.format_actions.insert_text_at_cursor("### "))
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["bold"], lambda: self.format_actions.insert_wrapped_text("**", "**"))
		format_menu.addAction(translations[self.current_language]["italic"], lambda: self.format_actions.insert_wrapped_text("*", "*"))
		format_menu.addAction(translations[self.current_language]["strikethrough"], lambda: self.format_actions.insert_wrapped_text("~~", "~~"))
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["bullet_list"], lambda: self.format_actions.insert_text_at_cursor("- "))
		format_menu.addAction(translations[self.current_language]["numbered_list"], lambda: self.format_actions.insert_text_at_cursor("1. "))
		format_menu.addAction(translations[self.current_language]["task_list"], lambda: self.format_actions.insert_text_at_cursor("- [ ] "))
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["link"], lambda: self.format_actions.insert_text_at_cursor("[Link Text](http://)"))
		format_menu.addAction(translations[self.current_language]["image"], lambda: self.format_actions.insert_text_at_cursor("![Alt Text](url)"))
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["inline_code"], lambda: self.format_actions.insert_wrapped_text("`", "`"))
		format_menu.addAction(translations[self.current_language]["keyboard_key"], lambda: self.format_actions.insert_wrapped_text("<kbd>", "</kbd>"))
		format_menu.addAction(translations[self.current_language]["code_block"], lambda: self.format_actions.insert_text_at_cursor("```\n\n```"))
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["blockquote"], lambda: self.format_actions.insert_text_at_cursor("> "))
		format_menu.addAction(translations[self.current_language]["horizontal_line"], lambda: self.format_actions.insert_text_at_cursor("\n---\n"))
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["table"], self.insert_table_dialog)
		format_menu.addAction(translations[self.current_language]["math_formula"], self.insert_math_equation)
		# تم إضافة ميزة وسم الملاحظات هنا
		format_menu.addSeparator()
		format_menu.addAction(translations[self.current_language]["notes_tag"], self.insert_note)

		format_action = QAction(translations[self.current_language]["format"], self)
		format_action.setMenu(format_menu)
		self.toolbar.addAction(format_action)

		self.toolbar.addSeparator()

		find_replace_action = QAction(translations[self.current_language]["find_replace_title"], self)
		find_replace_action.triggered.connect(self.search_replace.show_find_replace_dialog)
		self.toolbar.addAction(find_replace_action)

		self.toolbar.addSeparator()

		text_menu = QMenu(translations[self.current_language]["text"], self)
		text_menu.addAction(translations[self.current_language]["to_uppercase"], lambda: self.format_actions.convert_case("upper"))
		text_menu.addAction(translations[self.current_language]["to_lowercase"], lambda: self.format_actions.convert_case("lower"))
		text_action = QAction(translations[self.current_language]["text"], self)
		text_action.setMenu(text_menu)
		self.toolbar.addAction(text_action)

		self.toolbar.addSeparator()

		export_html_action = QAction(translations[self.current_language]["export_html"], self)
		export_html_action.triggered.connect(self.export_to_html)
		self.toolbar.addAction(export_html_action)

		self.toolbar.addSeparator()

		toggle_theme_action = QAction(translations[self.current_language]["toggle_theme"], self)
		toggle_theme_action.triggered.connect(self.theme_manager.toggle_theme)
		self.toolbar.addAction(toggle_theme_action)

		help_action = QAction(translations[self.current_language]["help"], self)
		help_action.triggered.connect(self.show_help)
		self.toolbar.addAction(help_action)

		self.toolbar.addSeparator()

		language_menu = QMenu(translations[self.current_language]["language"], self)
		en_action = QAction("English", self)
		ar_action = QAction("العربية", self)
		zh_action = QAction("中文", self)
		es_action = QAction("Español", self)
		language_menu.addAction(en_action)
		language_menu.addAction(ar_action)
		language_menu.addAction(zh_action)
		language_menu.addAction(es_action)

		en_action.triggered.connect(lambda: self.change_language("en"))
		ar_action.triggered.connect(lambda: self.change_language("ar"))
		zh_action.triggered.connect(lambda: self.change_language("zh"))
		es_action.triggered.connect(lambda: self.change_language("es"))

		language_action = QAction(translations[self.current_language]["language"], self)
		language_action.setMenu(language_menu)
		self.toolbar.addAction(language_action)

	def insert_table_dialog(self):
		dialog = TableCreationDialog(self, self.current_language)
		if dialog.exec_() == QDialog.Accepted:
			rows, cols = dialog.get_table_dimensions()
			markdown_table = generate_markdown_table(rows, cols, self.current_language)
			self.format_actions.insert_text_at_cursor(markdown_table)
			self.statusBar_message.showMessage(translations[self.current_language]["table_inserted"].format(rows, cols))

	def insert_math_equation(self):
		editor = self.get_current_editor()
		if not editor:
			return

		selected_text = editor.textCursor().selectedText()
		if not selected_text:
			text_to_insert = "$$"
			editor.insertPlainText(text_to_insert)
			cursor = editor.textCursor()
			cursor.movePosition(QTextCursor.PreviousCharacter, QTextCursor.MoveAnchor, 1)
			editor.setTextCursor(cursor)
		else:
			editor.insertPlainText("$$" + selected_text + "$$")
			
		self.statusBar_message.showMessage(translations[self.current_language]["math_formula_inserted"])

	def update_counts(self, text_content):
		if text_content is None:
			text_content = ""
		words = len(text_content.split())
		chars = len(text_content)
		if hasattr(self, 'word_count_label') and self.word_count_label is not None:
			self.word_count_label.setText(translations[self.current_language]["word_count"].format(words))
		if hasattr(self, 'char_count_label') and self.char_count_label is not None:
			self.char_count_label.setText(translations[self.current_language]["char_count"].format(chars))

	def update_preview_and_counts(self):
		editor = self.get_current_editor()
		preview = self.get_current_preview()
		if not editor or not preview: return

		raw_text = editor.toPlainText()
		html = markdown.markdown(raw_text, extensions=['fenced_code', 'tables', 'codehilite', 'toc', 'markdown_checklist.extension', 'footnotes','extra'])
		
		html = re.sub(r'~~(.*?)~~', r'<del>\1</del>', html)
		
		html = re.sub(r'<li>\s*\[\s*\]\s*(.*?)</li>', r'<li>☐ \1</li>', html)
		html = re.sub(r'<li>\s*\[\s*x\s*\]\s*(.*?)</li>', r'<li>✅ \1</li>', html)
		
		html = re.sub(
			r'<img(.*?)(/?)>',
			r'<img\1 style="max-width:200px; height:auto;"\2>',
			html
		)

		
		html = html.replace('<li><p>[ ]', '<li><p>☐')
		html = html.replace('<li><p>[x]', '<li><p>✅')

		if self.theme_manager.is_dark_theme:
			text_color = "#f0f0f0"
			link_color = "#99c1ff"
			border_color = "#555"
			header_bg = "#444"
			code_bg = "#3a3a3a"
			kbd_bg = "#2b2b2b"
			kbd_border = "#4b4b4b"
			footnote_link_color = "#99c1ff"
			footnote_border = "#444"
			footnote_hr = "#666"
		else:
			text_color = "#000000"
			link_color = "#0000ee"
			border_color = "#ddd"
			header_bg = "#f2f2f2"
			code_bg = "#eaeaea"
			kbd_bg = "#f8f8f8"
			kbd_border = "#ccc"
			footnote_link_color = "#0000ee"
			footnote_border = "#ccc"
			footnote_hr = "#ccc"

		
		css_style = f"""
			<style>
				body {{
					font-family: Arial, sans-serif;
					color: {text_color};
				}}
				a {{
					color: {link_color};
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
				kbd {{
					font-family: monospace;
					padding: 2px 4px;
					border: 1px solid {kbd_border};
					border-radius: 3px;
					background-color: {kbd_bg};
					font-size: 0.9em;
					color: {text_color};
					white-space: nowrap;
					box-shadow: 0 1px 0 rgba(0, 0, 0, 0.2), 0 0 0 2px #fff inset;
				}}
				
				.footnote-ref a {{
					color: {footnote_link_color};
					font-size: 0.8em;
					text-decoration: none;
				}}
				.footnote-backref {{
					font-size: 0.8em;
				}}
				.footnote-backref a {{
					color: {footnote_link_color};
					text-decoration: none;
				}}
				hr.footnotes-sep {{
					border: 0;
					height: 1px;
					background-color: {footnote_hr};
					margin-top: 20px;
					margin-bottom: 20px;
				}}

				del {{
					text-decoration: line-through;
					color: inherit;
				}}
			</style>
		<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
		<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
		"""
		preview.setHtml(css_style + html)
		self.update_counts(raw_text)
		
		current_editor = self.get_current_editor()
		if current_editor:
			self.file_manager.set_tab_modified_by_editor(current_editor, True)
			
	def update_window_title(self):
		base_title = translations[self.current_language]["app_title"]
		current_file = self.get_current_file()
		if current_file:
			file_name = os.path.basename(current_file)
			self.setWindowTitle(f"{base_title} - {file_name}")
		else:
			self.setWindowTitle(base_title)

	def show_help(self):
		help_text = translations[self.current_language]["help_text"]
		QMessageBox.information(self, translations[self.current_language]["help"], help_text)

	def export_to_html(self):
		current_preview = self.get_current_preview()
		if not current_preview:
			QMessageBox.warning(self, translations[self.current_language]["error"], translations[self.current_language]["no_content_to_export"])
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
				QMessageBox.warning(self, translations[self.current_language]["error"], translations[self.current_language]["export_error"].format(str(e)))
	
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
					self.theme_manager.update_single_tab_preview(container_widget.editor, container_widget.preview)

		if self.search_replace.find_replace_dialog:
			self.search_replace.find_replace_dialog.update_language(self.current_language)
		self.update_status_bar_for_current_tab()
	
	def insert_note(self):
		editor = self.get_current_editor()
		if not editor:
			return
		
		note_text = "> [!NOTE]> P.S goes here ."
		editor.insertPlainText(note_text)
		self.statusBar_message.showMessage(translations[self.current_language]["notes_inserted"])

	def closeEvent(self, event):
		self.file_manager.closeEvent(event)
