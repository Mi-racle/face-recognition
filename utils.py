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


def encode_face(img: np.ndarray, model_name='Dlib'):
    model: FacialRecognition = modeling.build_model(
        task='facial_recognition', model_name=model_name
    )
    target_size = model.input_shape

    # img = face[:, :, ::-1]
    img = img / 255

    img = preprocessing.resize_image(
        img=img,
        target_size=(target_size[1], target_size[0]),
    )
    img = preprocessing.normalize_input(img=img, normalization='base')

    return model.forward(img)
