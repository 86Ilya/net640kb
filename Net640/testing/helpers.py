from io import BytesIO
from PIL import Image


def create_test_image(side_len=50):
    # TODO create big jpeg files
    file = BytesIO()
    image = Image.new('RGB', size=(side_len, side_len), color=(155, 0, 0))
    image.save(file, 'BMP')
    file.name = 'test.bmp'
    file.seek(0)
    content_type = 'image/bmp'
    return file, content_type
