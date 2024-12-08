from time import time

import cv2
import numpy as np
from deepface import DeepFace

from static_anti import static_detect
from db.feature import get_all_features
from utils import euclidean_distance, cosine_similarity


def str2ndarray(string: str):
    string = string[1: -1]
    decimals = string.split(',')
    decimals = np.array(decimals)

    return decimals.astype(dtype=np.float64)


def run():
    all_features = get_all_features()
    names = []
    encodings = []

    for feature in all_features:
        names.append(feature[1])
        encodings.append(str2ndarray(feature[2]))

    cap = cv2.VideoCapture('images/test.mp4')
    # cap = cv2.VideoCapture(0)

    count = 0
    while True:
        st = time()
        ret, frame = cap.read()
        frame_to_show = frame.copy()

        try:
            det_st = time()
            faces = DeepFace.represent(frame, model_name='Dlib', detector_backend='retinaface')
            # static_dict = static_detect(frame)
            # image_box = static_dict['bbox']
            # cropped_frame = frame
            det_et = time()
            print(f'Face detection cost: {det_et - det_st} s')

            for face in faces:
                location = face['facial_area']
                embedding = face['embedding']
                bbox = [
                    location['x'],
                    location['y'],
                    location['w'],
                    location['h']
                ]

                liv_st = time()
                static_dict = static_detect(frame, bbox)
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
    run()
