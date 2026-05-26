import sys
from PySide6.QtWidgets import QApplication

from app.ui.windows.main_window import MainScreen


def main():
    app = QApplication(sys.argv)

    main_app = MainScreen()
    main_app.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()