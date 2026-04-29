import sys
from PyQt6.QtWidgets import QApplication
from ui_main import AudioTranslatorApp

def main():
    app = QApplication(sys.argv)
    window = AudioTranslatorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()