import sys

from PySide6.QtWidgets import QApplication

from app.infrastructure.database.migrations import (
    run_migrations,
)
from app.ui.windows.main_window import MainScreen


def main():
    try:
        run_migrations()
        print("Database updated successfully.")

    except Exception as error:
        print(f"Migration error: {error}")
        return

    app = QApplication(sys.argv)

    main_window = MainScreen()
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()