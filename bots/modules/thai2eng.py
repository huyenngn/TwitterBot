from io import BytesIO
import os
from urllib.parse import urlencode
import requests
from bots.modules.util import img2byte
from PIL import Image

keys = ["API_FLASH_KEY", "API_FLASH_KEY2"]


class Thai2Eng:
    def __init__(self):
        self.key = 0
        self.api_flash_key = os.getenv(keys[0])

    def get_new_key(self):
        self.key = self.key + 1 if self.key < len(keys) - 1 else 0
        return self.key

    def get_definition(self, text):
        params = urlencode(
            dict(
                access_key=self.api_flash_key,
                wait_until="page_loaded",
                width="750",
                full_page="true",
                js="document.getElementsByClassName('container')[0].setAttribute('style', 'display: none;');document.querySelectorAll('footer')[0].setAttribute('hidden', 'true');document.querySelectorAll('form')[0].setAttribute('hidden', 'true');",
                quality="100",
                url="https://thai2english.com/?q=" + text,
            )
        )

        img = requests.get("https://api.apiflash.com/v1/urltoimage?" + params)

        if img.status_code >= 400:
            self.api_flash_key = os.getenv(keys[self.get_new_key()])
            return self.get_definition(text)

        pil_image = Image.open(BytesIO(img.content))
        width, height = pil_image.size
        parts = (4 if height > 3000 else (3 if height > 2500 else (2 if height > 1500 else 1)))
        pages = []
        for i in range(0, parts):
            crop = pil_image.crop((0, i * height / parts, width, (i + 1) * height / parts))
            pages.append(img2byte(crop))

        return pages
