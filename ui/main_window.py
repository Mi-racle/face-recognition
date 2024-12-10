import ctypes

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QTabWidget, QTextEdit
from typing_extensions import override

from ui.recognition_window import RecognitionWindow
from ui.registration_window import RegistrationWindow


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        user32 = ctypes.windll.user32
        screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        self.setWindowTitle('人脸识别系统Demo')
        self.setGeometry(100, 100, screen_width // 2, screen_height // 2)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.registration_window = RegistrationWindow()
        self.recognition_window = RecognitionWindow()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.registration_window, '人脸注册')
        self.tab_widget.addTab(self.recognition_window, '人脸识别')

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(layout)

    @override
    def closeEvent(self, event):
        self.registration_window.closeStream()
