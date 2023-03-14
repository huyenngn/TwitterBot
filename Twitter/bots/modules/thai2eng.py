from io import BytesIO
import os
from urllib.parse import urlencode
import requests
from bots.modules.util import img2byte
from PIL import Image

keys = ["API_FLASH_KEY", "API_FLASH_KEY2", "API_FLASH_KEY3"]


class Thai2Eng:
    def __init__(self):
        self.key = 0
        self.retries = 0
        self.api_flash_key = os.getenv(keys[0])

    def get_new_key(self):
        self.key = self.key + 1 if self.key < len(keys) - 1 else 0
        self.api_flash_key = os.getenv(keys[self.key])

    def get_definition(self, text):
        params = urlencode(
            dict(
                access_key=self.api_flash_key,
                wait_until="network_idle",
                width="750",
                full_page="true",
                js="let list = document.querySelectorAll('ul'); if ( list.length == 0 || list[0].children.length == 0){document.querySelector('body').setAttribute('style', 'display: none;')} else {document.getElementsByClassName('container')[0].setAttribute('style', 'display: none;');document.querySelector('footer').setAttribute('hidden', 'true');document.querySelector('form').setAttribute('hidden', 'true');};",
                quality="100",
                url="https://thai2english.com/?q=" + text,
            )
        )

        img = requests.get("https://api.apiflash.com/v1/urltoimage?" + params)
        pages = []
        if img.status_code != 200:
            self.get_new_key()
            if self.retries < len(keys):
                self.retries += 1
                return self.get_definition(text)
            else:
                return pages

        self.retries = 0
        pil_image = Image.open(BytesIO(img.content))
        width, height = pil_image.size
        parts = (4 if height > 3000 else (3 if height > 2500 else (2 if height > 1500 else 1)))
        for i in range(0, parts):
            crop = pil_image.crop((0, i * height / parts, width, (i + 1) * height / parts))
            pages.append(img2byte(crop))

        return pages
