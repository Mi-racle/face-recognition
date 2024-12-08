import os

import numpy as np
from deepface import DeepFace

from db.feature import insert_feature, feature_exists


def do_insert(input_dir):
    if not os.path.exists(input_dir):
        os.mkdir(input_dir)

    filenames = os.listdir(input_dir)

    for filename in filenames:
        if feature_exists(os.path.splitext(filename)[0]):
            continue

        file_path = f'{input_dir}/{filename}'

        try:
            faces = DeepFace.represent(file_path, model_name='Dlib', detector_backend='dlib')
            if len(faces) <= 0:
                continue
            face = faces[0]
            embedding = face['embedding']
            embedding = np.array(embedding)
            insert_feature(os.path.splitext(filename)[0], embedding)

        except ValueError as e:
            print('No face detected')


if __name__ == '__main__':
    do_insert('transformed_images')
    # do_insert('images')
