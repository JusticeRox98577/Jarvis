import sys

from PySide6.QtWidgets import QApplication

from jarvis.config import load_config
from jarvis.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("J.A.R.V.I.S.")
    cfg = load_config()
    window = MainWindow(cfg)
    window.resize(1280, 780)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
