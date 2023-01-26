import logging
# import cv2 as cv
import numpy as np
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def url2img(url):
    response = requests.get(url)
    img = np.asarray(bytearray(response.content), dtype="uint8")
    # img = cv.imdecode(img, cv.IMREAD_COLOR)

    return img

