import os
import secrets
from PIL import Image
from library import app


def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_image.filename)
    image_file = random_hex + file_ext
    image_path = os.path.join(app.root_path, 'static/image', image_file)

    output_size = (450, 300)
    output_image = Image.open(form_image)
    output_image.thumbnail = output_size
    output_image.save(image_path)
    return image_file