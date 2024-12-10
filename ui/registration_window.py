import os
import threading
from typing import Union

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QFileDialog, QMessageBox
from deepface import DeepFace
from typing_extensions import override

from db.feature import insert_feature


class RegistrationWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.__display_label = ImageLabel()
        self.__display_label.setText('图像采集区')
        self.__display_label.setStyleSheet("QLabel {background-color: grey;}")

        self.__stream_button = QPushButton('读取视频流')
        self.__stream_button.clicked.connect(lambda: self._onStreamButtonClicked(0))

        self.__shot_button = QPushButton('截图并保存')
        self.__shot_button.clicked.connect(self._onShotButtonClicked)

        self.__register_button = QPushButton('注册面容')
        self.__register_button.clicked.connect(self._onRegisterButtonClicked)

        layout = QGridLayout()

        layout.addWidget(self.__display_label, 0, 0, 10, 6)
        layout.addWidget(self.__stream_button, 0, 6, 1, 1)
        layout.addWidget(self.__shot_button, 1, 6, 1, 1)
        layout.addWidget(self.__register_button, 2, 6, 1, 1)

        self.setLayout(layout)

        self.__stream_button_flipped = False
        self.__cap = None
        self.__cap_on = False

    def _onStreamButtonClicked(self, source: Union[int, str]):
        if not self.__stream_button_flipped:
            self.openStream(source)
            self.__stream_button.setText('关闭视频流')
        else:
            self.closeStream()
            self.__stream_button.setText('读取视频流')

        self.__stream_button_flipped = not self.__stream_button_flipped

    def _onShotButtonClicked(self):
        frame = self.__display_label.frame

        if frame is None:
            QMessageBox.critical(self, '错误', '请确保图像采集区存在图像！')
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '选择图片保存路径',
            'images/untitled.png',
            'Images (*.png *.jpg *.bmp)'
        )
        if file_path:
            cv2.imwrite(file_path, frame)

    def _onRegisterButtonClicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择图片',
            '',
            'Images (*.png *.jpg *.bmp)'
        )
        if file_path:
            frame = cv2.imread(file_path)
            faces = DeepFace.represent(frame, model_name='Dlib', detector_backend='retinaface')
            embedding = np.array(faces[0]['embedding'])
            insert_feature(os.path.splitext(os.path.basename(file_path))[0], embedding)

    def openStream(self, source: Union[int, str]):
        self.__cap = cv2.VideoCapture(source)
        self.__cap_on = True

        def updateLabel():
            while self.__cap_on:
                ret, frame = self.__cap.read()
                if ret:
                    self.__display_label.setUMat(frame)
                else:
                    self.closeStream()
                    break
                cv2.waitKey(10)

            self.__cap.release()
            self.__cap = None

        t = threading.Thread(target=updateLabel)
        t.start()

    def closeStream(self):
        self.__cap_on = False


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.__umat = None
        self.frame = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__pixmap = QPixmap().scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(self.__pixmap)

    def setUMat(self, umat):
        self.__umat = umat
        self.frame = umat
        self._shapeUMat()
        self._shapeFrame()
        img_rgb = cv2.cvtColor(self.__umat, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qimage = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.__pixmap = QPixmap.fromImage(qimage).scaled(
            self.size().width(),
            self.size().height() - 1,
            Qt.AspectRatioMode.IgnoreAspectRatio
        )
        self.setPixmap(self.__pixmap)

    def _shapeUMat(self):
        d_h, d_w = self.size().height() - 1, self.size().width()
        o_h, o_w, _ = self.__umat.shape

        if o_h > d_h:
            self.__umat = self.__umat[o_h - d_h:, ]
        elif o_h < d_h:
            v_padding = np.full((d_h - o_h, o_w, 3), 0, dtype=np.uint8)
            self.__umat = np.concatenate((v_padding, self.__umat), axis=0)

        if o_w > d_w:
            start_x = (o_w - d_w) // 2
            self.__umat = self.__umat[:, start_x: start_x + d_w]
        elif o_w < d_w:
            p0_w = (d_w - o_w) // 2
            p1_w = d_w - o_w - p0_w
            h_padding0 = np.full((d_h, p0_w, 3), 0, dtype=np.uint8)
            h_padding1 = np.full((d_h, p1_w, 3), 0, dtype=np.uint8)
            self.__umat = np.concatenate((h_padding0, self.__umat, h_padding1), axis=1)

    def _shapeFrame(self):
        d_h, d_w = self.size().height() - 1, self.size().width()
        o_h, o_w, _ = self.frame.shape

        if o_h > d_h:
            self.__umat = self.__umat[o_h - d_h:, ]

        if o_w > d_w:
            start_x = (o_w - d_w) // 2
            self.__umat = self.__umat[:, start_x: start_x + d_w]

    @override
    def resizeEvent(self, event):
        if not self.__pixmap.isNull():
            self._shapeUMat()
            self.setUMat(self.__umat)

        super().resizeEvent(event)
