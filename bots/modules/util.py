from io import BytesIO
from PIL import Image


def img2byte(pil_image):
    buff = BytesIO()
    pil_image.save(buff, format="JPEG")
    return buff.getvalue()


def byte2img(byte):
    Image.open(BytesIO(byte))
