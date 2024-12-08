from PyQt6.QtWidgets import QWidget, QVBoxLayout


class RecognitionWindow(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(100)

        self.setLayout(layout)
