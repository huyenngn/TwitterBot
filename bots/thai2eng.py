import os
from urllib.parse import urlencode
import requests
from io import BytesIO
from PIL import Image

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

    return requests.get("https://api.apiflash.com/v1/urltoimage?" + params)


def main():
    response = get_definition(
        "สวัสดีค่า หนูชื่อน้องชานม🧋 ขี้อ้อน อยู่ไม่ค่อยนิ่ง ยิ้มทั้งวันทั้งคืน ซนบ้างง แหะๆ มารู้จักกันมั้ยคะ🤏🏻😜💖  "
    )
    pil_image = Image.open(BytesIO(response))
    pil_image.show()


if __name__ == "__main__":
    main()
