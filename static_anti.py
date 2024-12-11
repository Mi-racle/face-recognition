import os
from time import time

import cv2
import numpy as np

from static_pack.anti_spoofer import AntiSpoofer
from static_pack.crop import CropImage
from static_pack.utils import parse_model_name


def static_detect(
        image_src,
        image_bbox=None,
        model_dir='models/anti_spoof_models',
        device_id=0
):
    model_test = AntiSpoofer(device_id)
    image_cropper = CropImage()
    image = cv2.imread(image_src) if type(image_src) is str else image_src
    image_bbox = model_test.get_bbox(image)  # [x, y, w, h]
    prediction = np.zeros((1, 3))
    # sum the prediction from single model's result
    for model_name in os.listdir(model_dir):
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            'org_img': image,
            'bbox': image_bbox,
            'scale': scale,
            'out_w': w_input,
            'out_h': h_input,
            'crop': True,
        }
        if scale is None:
            param['crop'] = False
        img = image_cropper.crop(**param)
        prediction += model_test.predict(img, os.path.join(model_dir, model_name))

    # draw result of prediction
    label = np.argmax(prediction)
    conf = prediction[0][label] / 2
    real_flag = True if label == 1 else False

    # if label == 1:
    #     result_text = f'RealFace Score: {conf:.2f}'
    #     color = (255, 0, 0)
    # else:
    #     result_text = f'FakeFace Score: {conf:.2f}'
    #     color = (0, 0, 255)
    #
    # cv2.rectangle(
    #     image,
    #     (image_bbox[0], image_bbox[1]),
    #     (image_bbox[0] + image_bbox[2], image_bbox[1] + image_bbox[3]),
    #     color,
    #     thickness=2
    # )
    # cv2.putText(
    #     image,
    #     result_text,
    #     (image_bbox[0], image_bbox[1] - 5),
    #     cv2.FONT_HERSHEY_COMPLEX,
    #     0.5 * image.shape[0] / 1024,
    #     color
    # )

    cv2.imwrite('runs/out.jpg', image)

    return {
        'bbox': image_bbox,
        'real': real_flag,
        # 'conf': conf
    }
