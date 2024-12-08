import os
import random

from PIL import Image, ImageEnhance


def random_transform(image):
    angle = random.uniform(-30, 30)  # 随机旋转角度范围为 -30 到 30 度
    image = image.rotate(angle)

    if random.choice([True, False]):
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    enhancer = ImageEnhance.Brightness(image)
    factor = random.uniform(0.5, 1.5)  # 随机亮度因子
    image = enhancer.enhance(factor)

    scale_factor = random.uniform(0.8, 1.2)  # 随机缩放因子
    width, height = image.size
    new_size = (int(width * scale_factor), int(height * scale_factor))
    image = image.resize(new_size)

    tx, ty = random.randint(-10, 10), random.randint(-10, 10)  # 随机平移范围
    image = image.transform(image.size, Image.AFFINE, (1, 0, tx, 0, 1, ty))

    return image


input_image_path = "images/lpk.jpg"
image = Image.open(input_image_path)

output_dir = "transformed_images"
os.makedirs(output_dir, exist_ok=True)

for i in range(1000):
    transformed_image = random_transform(image)
    transformed_image.save(os.path.join(output_dir, f"transformed_{str(i + 1).zfill(4)}.jpg"))

print("1000张变换后的图片已经生成并保存。")
