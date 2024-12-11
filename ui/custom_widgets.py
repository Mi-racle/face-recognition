from typing_extensions import override

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QLabel


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.__umat = None
        self.frame = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__pixmap = QPixmap().scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setPixmap(self.__pixmap)

    def set_umat(self, umat, update_frame=True):
        self.__umat = umat
        self._shape_umat()

        if update_frame:
            self.frame = umat
            self._shape_frame()

    def display_umat(self):
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

    def _shape_umat(self):
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

    def _shape_frame(self):
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
            self._shape_umat()
            self.set_umat(self.__umat)
            self.display_umat()

        super().resizeEvent(event)
