import cv2
import numpy as np
from deepface.models.FacialRecognition import FacialRecognition
from deepface.modules import modeling, preprocessing


def euclidean_distance(v1, v2):
    return np.linalg.norm(v1 - v2)


def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)


def str2ndarray(string: str):
    string = string[1: -1]
    decimals = string.split(',')
    decimals = np.array(decimals)

    return decimals.astype(dtype=np.float64)


def get_eyes(img: np.ndarray) -> list[tuple]:
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eye_cascade.detectMultiScale(img, 1.3, 10)

    eye_coords = []
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(img, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 1)
        eye_coords.append((ey, ex))

    return eye_coords


def encode_face(img: np.ndarray, model_name='Dlib') -> list[float]:
    model: FacialRecognition = modeling.build_model(
        task='facial_recognition', model_name=model_name
    )
    target_size = model.input_shape

    # TODO
    # align img according to eyes

    # img = face[:, :, ::-1]
    # img should be bgr
    img = img / 255

    img = preprocessing.resize_image(
        img=img,
        target_size=(target_size[1], target_size[0]),
    )
    img = preprocessing.normalize_input(img=img, normalization='base')

    return model.forward(img)
