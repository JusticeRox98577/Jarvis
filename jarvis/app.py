import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from jarvis.config import load_config, resolve_asset
from jarvis.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("J.A.R.V.I.S.")

    icon_path = resolve_asset("jarvis.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    cfg = load_config()
    window = MainWindow(cfg)
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.resize(1280, 780)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
