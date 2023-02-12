import os
from urllib.parse import urlencode
import requests
from helpers import img2byte, byte2img

api_flash_key = os.getenv("API_FLASH_KEY")


def get_definition(text):
    params = urlencode(
        dict(
            access_key=api_flash_key,
            wait_until="page_loaded",
            width="750",
            full_page="true",
            js="document.getElementsByClassName('container')[0].setAttribute('style', 'display: none;');document.querySelectorAll('footer')[0].setAttribute('hidden', 'true');document.querySelectorAll('form')[0].setAttribute('hidden', 'true');",
            quality="100",
            url="https://thai2english.com/?q=" + text,
        )
    )

    img = requests.get("https://api.apiflash.com/v1/urltoimage?" + params)

    pages = []
    if img.status_code >= 400:
        return pages

    pil_image = byte2img(img.content)
    width, height = pil_image.size
    parts = (
        4 if height > 3000 else (3 if height > 2500 else (2 if height > 1500 else 1))
    )
    for i in range(0, parts):
        crop = pil_image.crop((0, i * height / parts, width, (i + 1) * height / parts))
        pages.append(img2byte(crop))

    return pages
