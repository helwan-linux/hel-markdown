import sys
from PyQt5.QtWidgets import QApplication
from editor import MarkdownEditor

def main():
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.showMinimized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
