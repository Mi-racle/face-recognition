from time import time
from typing import Union

import cv2
import numpy as np
from deepface import DeepFace

from static_anti import static_detect
from db.feature import get_all_features
from utils import cosine_similarity, str2ndarray, encode_face, get_eyes


def detect_image(image: Union[str, np.ndarray], names=None, encodings=None):
    if not names or not encodings:
        names = []
        encodings = []
        all_features = get_all_features()
        for feature in all_features:
            names.append(feature[1])
            encodings.append(str2ndarray(feature[2]))

    st = time()

    if isinstance(image, str):
        image = cv2.imread(image)
    frame_to_show = image.copy()

    det_st = time()
    faces = DeepFace.represent(image, model_name='Dlib', detector_backend='retinaface')
    # static_dict = static_detect(frame)
    # image_box = static_dict['bbox']
    # cropped_frame = frame
    det_et = time()
    print(f'Face detection cost: {det_et - det_st} s')

    for face in faces:
        location = face['facial_area']
        # y, x, h, w = location['y'], location['x'], location['h'], location['w']
        # fac = image[y: y + h, x: x + w]
        # ef = time()
        # encode_face(fac)
        # print(f'encode face cost: {time() - ef}')
        embedding = face['embedding']
        bbox = [
            location['x'],
            location['y'],
            location['w'],
            location['h']
        ]

        liv_st = time()
        static_dict = static_detect(image, bbox)
        liv_et = time()
        print(f'Livingness detection cost: {liv_et - liv_st} s')

        idx = -1

        # shortest_dis = float('inf')
        # for _id, encoding in enumerate(encodings):
        #     dis = euclidean_distance(embedding, encoding)
        #     if dis <= shortest_dis:
        #         shortest_dis = dis
        #         idx = _id

        comp_st = time()
        biggest_sim = -1
        for _id, encoding in enumerate(encodings):
            sim = cosine_similarity(embedding, encoding)
            if sim >= biggest_sim:
                biggest_sim = sim
                idx = _id
        comp_et = time()
        print(f'Comparison cost: {comp_et - comp_st} s')

        if idx < 0:
            cv2.imshow('video', frame_to_show)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        name = names[idx]

        left = location['x']
        top = location['y']
        right = left + location['w']
        bottom = top + location['h']
        cv2.rectangle(frame_to_show, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame_to_show, (left, top), (right, top + 35), (0, 0, 255), cv2.FILLED)
        cv2.putText(
            frame_to_show,
            f'{"Real" if static_dict["real"] else "Fake"}Face {name} Score: {static_dict["conf"]:.2f}',
            (left + 6, top + 22),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65 * frame_to_show.shape[0] / 1080,
            (255, 0, 0) if static_dict['real'] else (255, 255, 255),
            1
        )

    et = time()
    print(f'Total cost: {et - st} s\n')


def recognize_image(image: Union[str, np.ndarray], names=None, encodings=None):
    st = time()

    if not names or not encodings:
        names = []
        encodings = []
        all_features = get_all_features()
        for feature in all_features:
            names.append(feature[1])
            encodings.append(str2ndarray(feature[2]))

    if isinstance(image, str):
        image = cv2.imread(image)

    static_dict = static_detect(image)

    et = time()

    if static_dict['bbox'] == [0, 0, 1, 1]:  # No face detected
        return {
            'name': 'No face',
            'conf': -2,
            'cost': et - st,
            **static_dict
        }

    x, y, w, h = static_dict['bbox']
    face_image = image[y: y + h, x: x + w]
    embedding = encode_face(face_image)
    biggest_sim = -1
    idx = -1
    for _id, encoding in enumerate(encodings):
        sim = cosine_similarity(embedding, encoding)
        if sim >= biggest_sim:
            biggest_sim = sim
            idx = _id

    et = time()

    if idx < 0:
        name = 'No match'
        conf = -1
    else:
        name = names[idx]
        conf = (biggest_sim + 1) / 2

    ret_dict = {
        'name': name,
        'conf': conf,
        'cost': et - st,
        **static_dict
    }

    return ret_dict


def detect_stream(source: Union[int, str]):
    all_features = get_all_features()
    names = []
    encodings = []

    for feature in all_features:
        names.append(feature[1])
        encodings.append(str2ndarray(feature[2]))

    # cap = cv2.VideoCapture('images/test.mp4')
    cap = cv2.VideoCapture(source)

    count = 0
    while True:
        ret, frame = cap.read()
        frame_to_show = frame.copy()

        try:
            detect_image(frame, names, encodings)

        except ValueError as e:
            print('No face detected')

        cv2.imwrite(f'runs/{count}.jpg', frame_to_show)
        count += 1

        cv2.imshow('video', frame_to_show)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # detect_image('images/lpk.jpg')
    # detect_stream(0)
    print(recognize_image('images/lpk.jpg'))
