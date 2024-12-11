import threading
from typing import Union

import cv2
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel

from run import recognize_image
from ui.custom_widgets import ImageLabel


class RecognitionWindow(QWidget):

    stream_button_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.__display_label = ImageLabel()
        self.__display_label.setText('图像采集区')
        self.__display_label.setStyleSheet("QLabel {background-color: grey;}")

        self.__stream_button = QPushButton('开始识别')
        self.__stream_button.clicked.connect(lambda: self._on_stream_button_clicked(0))

        self.__result_label = QLabel()
        self.__result_label.setText('实时识别结果')
        self.__result_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.__result_label.setStyleSheet("QLabel {background-color: #f0f0f0;}")

        layout = QGridLayout()

        layout.addWidget(self.__display_label, 0, 0, 10, 5)
        layout.addWidget(self.__stream_button, 0, 6, 1, 2)
        layout.addWidget(self.__result_label, 1, 6, 8, 2)

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
            self.__stream_button.setText('终止识别')
        else:
            self.close_stream()
            self.__stream_button.setText('开始识别')

        self.__stream_button_flipped = not self.__stream_button_flipped

    def _update_result_label(self, result: dict):
        if result['conf'] == -1:
            self.__result_label.setText(
                '实时识别结果：\n'
                '未找到匹配的面容数据！\n'
                f'耗时：{result["cost"]:.3} 秒'
            )
        elif result['conf'] == -2:
            self.__result_label.setText(
                '实时识别结果：\n'
                '未检测到面容！\n'
                f'耗时：{result["cost"]:.3} 秒'
            )
        else:
            self.__result_label.setText(
                '实时识别结果：\n'
                f'姓名：{result["name"]}\n'
                f'置信度：{result["conf"]:.3}\n'
                f'活脸：{"是" if result["real"] else "否"}\n'
                f'耗时：{result["cost"]:.3} 秒'
            )

    def _update_display_label(self, result: dict):
        if result['conf'] == -2:
            return

        frame = self.__display_label.frame
        x, y, w, h = result['bbox']
        left, top, right, bottom = x, y, x + w, y + h

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, top), (right, top + 35), (0, 0, 255), cv2.FILLED)
        cv2.putText(
            frame,
            f'{"Real" if result["real"] else "Fake"}Face {result["name"]} Score: {result["conf"]:.2f}',
            (left + 6, top + 22),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65 * frame.shape[0] / 1080,
            (255, 0, 0) if result['real'] else (255, 255, 255),
            1
        )

        self.__display_label.set_umat(frame, False)

    def open_stream(self, source: Union[int, str]):
        self.__cap = cv2.VideoCapture(source)
        self.__cap_on = True

        def update_label():
            while self.__cap_on:
                ret, frame = self.__cap.read()
                if ret:
                    self.__display_label.set_umat(frame)
                    ret_dict = recognize_image(self.__display_label.frame)
                    self._update_result_label(ret_dict)
                    self._update_display_label(ret_dict)
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
