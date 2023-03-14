from io import BytesIO


def img2byte(pil_image):
    buff = BytesIO()
    pil_image.save(buff, format="JPEG")
    return buff.getvalue()
