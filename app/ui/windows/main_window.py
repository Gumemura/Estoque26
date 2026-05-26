from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
)


class SecondScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Segunda Tela")
        self.resize(300, 200)

        layout = QVBoxLayout()

        texto = QLabel("Você abriu a segunda tela!")
        layout.addWidget(texto)

        self.setLayout(layout)


class MainScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tela Principal")
        self.resize(400, 300)

        layout = QVBoxLayout()

        button = QPushButton("Abrir nova tela")
        button.clicked.connect(self.open_second_screen)

        layout.addWidget(button)

        self.setLayout(layout)

        self.second_screen = None

    def open_second_screen(self):
        self.second_screen = SecondScreen()
        self.second_screen.show()