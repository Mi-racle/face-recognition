import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class RegistrationWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.display_label = ImageLabel()
        self.button = QPushButton('start')
        self.button.clicked.connect(self.open_camera)

        layout = QHBoxLayout()
        layout.setSpacing(100)

        layout.addWidget(self.display_label)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def open_camera(self, camera_id=0):
        cap = cv2.VideoCapture(camera_id)

        # while True:
        ret, frame = cap.read()
        self.display_label.setUMat(frame)
        cv2.waitKey(1)


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.umat = None
        self.o_umat = None
        self.o_width = 200
        self.o_height = 100
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixmap = QPixmap().scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(self.pixmap)

    def setUMat(self, umat, change_o=False):
        self.umat = umat
        if change_o:
            self.o_umat = umat.copy()
            self.o_width = umat.shape[1]
            self.o_height = umat.shape[0]
        img_rgb = cv2.cvtColor(umat, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimg).scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(self.pixmap)

    def resizeEvent(self, event):
        if not self.pixmap.isNull():
            self.umat = cv2.resize(self.umat, [self.size().width(), self.size().height()])
            self.o_umat = cv2.resize(self.o_umat, [self.size().width(), self.size().height()])
            self.setUMat(self.umat)

        super().resizeEvent(event)

