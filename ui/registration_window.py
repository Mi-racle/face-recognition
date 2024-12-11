import os
import threading
from typing import Union

import cv2
import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QFileDialog, QMessageBox
from deepface import DeepFace

from db.feature import insert_feature, feature_exists
from ui.custom_widgets import ImageLabel


class RegistrationWindow(QWidget):

    stream_button_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.__display_label = ImageLabel()
        self.__display_label.setText('图像采集区')
        self.__display_label.setStyleSheet("QLabel {background-color: grey;}")

        self.__stream_button = QPushButton('读取视频流')
        self.__stream_button.clicked.connect(lambda: self._on_stream_button_clicked(0))

        self.__shot_button = QPushButton('截图并保存')
        self.__shot_button.clicked.connect(self._on_shot_button_clicked)

        self.__register_button = QPushButton('注册面容')
        self.__register_button.clicked.connect(self._on_register_button_clicked)

        layout = QGridLayout()

        layout.addWidget(self.__display_label, 0, 0, 10, 5)
        layout.addWidget(self.__stream_button, 0, 6, 1, 2)
        layout.addWidget(self.__shot_button, 1, 6, 1, 2)
        layout.addWidget(self.__register_button, 2, 6, 1, 2)

        self.setLayout(layout)

        self.__stream_button_flipped = False
        self.__cap = None
        self.__cap_on = False

        self.stream_button_signal.connect(
            lambda: self._on_stream_button_clicked() if self.__stream_button_flipped else {}
        )

    def _on_stream_button_clicked(self, source: Union[int, str] = 0):
        if not self.__stream_button_flipped:
            self.open_stream(source)
            self.__stream_button.setText('关闭视频流')
        else:
            self.close_stream()
            self.__stream_button.setText('读取视频流')

        self.__stream_button_flipped = not self.__stream_button_flipped

    def _on_shot_button_clicked(self):
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

    def _on_register_button_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择图片',
            '',
            'Images (*.png *.jpg *.bmp)'
        )

        if file_path:
            personal_name = os.path.splitext(os.path.basename(file_path))[0]

            if not feature_exists(personal_name):
                frame = cv2.imread(file_path)
                faces = DeepFace.represent(frame, model_name='Dlib', detector_backend='retinaface')
                embedding = np.array(faces[0]['embedding'])
                insert_feature(personal_name, embedding)

            else:
                QMessageBox.warning(self, '警告', '所选面容已在数据库中！')

    def open_stream(self, source: Union[int, str]):
        self.__cap = cv2.VideoCapture(source)
        self.__cap_on = True

        def update_label():
            while self.__cap_on:
                ret, frame = self.__cap.read()
                if ret:
                    self.__display_label.set_umat(frame)
                    self.__display_label.display_umat()
                else:
                    self.close_stream()
                    break
                cv2.waitKey(10)

            self.__cap.release()
            self.__cap = None

        t = threading.Thread(target=update_label)
        t.start()

    def close_stream(self):
        self.__cap_on = False

