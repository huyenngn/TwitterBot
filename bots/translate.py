from io import BytesIO
import os
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
from google.cloud import vision
import requests
from setup import translation_settings

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = "twitterbot-376108"


def img2byte(pil_image):
    buff = BytesIO()
    pil_image.save(buff, format="JPEG")
    return buff.getvalue()


class ContentTranslator:
    def __init__(self):
        self.vision = vision.ImageAnnotatorClient()
        self.google = Translator()

    def translate_image(self, url):
        response = requests.get(url).content
        pil_image = Image.open(BytesIO(response))
        draw = ImageDraw.Draw(pil_image)

        image = vision.Image(content=response)

        data = self.vision.document_text_detection(image=image)

        for page in data.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    poly = []
                    for vertex in paragraph.bounding_box.vertices:
                        p = (vertex.x, vertex.y)
                        poly.append(p)
                    draw.polygon(poly, fill=(255, 255, 255))
                    p = []
                    for word in paragraph.words:
                        w = []
                        for symbol in word.symbols:
                            w.append(symbol.text)
                        p.append("".join(w))
                    text = " ".join(p)
                    text = self.translate_text(text)
                    text = text.replace(", ", ",\n")
                    text = text.replace(". ", ".\n")

                    poly_width = max(
                        [abs(poly[0][0] - poly[1][0]), abs(poly[0][0] - poly[3][0])]
                    )
                    poly_height = max(
                        [abs(poly[0][1] - poly[1][1]), abs(poly[0][1] - poly[3][1])]
                    )

                    fontsize = 13
                    font = ImageFont.truetype("NotoSerif-Regular.ttf", fontsize)
                    textsize = font.getsize_multiline(text)
                    while textsize[0] < poly_width and textsize[1] < poly_height:
                        fontsize += 1
                        font = ImageFont.truetype("NotoSerif-Regular.ttf", fontsize)
                        textsize = font.getsize_multiline(text)

                    bbox = draw.multiline_textbbox(poly[0], text, font=font)
                    draw.rectangle(bbox, fill=(255, 255, 255))
                    draw.multiline_text(poly[0], text, (0, 0, 0), font=font)
        pil_image.show()

        return img2byte(pil_image)

    def translate_text(self, text):
        if not text:
            return ""

        translation = text
        for th, en in translation_settings["glossary"].items():
            translation = translation.replace(th, en)

        translation = self.google.translate(
            translation,
            src=translation_settings["src"],
            dst=translation_settings["dst"],
        ).text

        for src, dst in translation_settings["corrections"].items():
            translation = translation.replace(src, dst)
        return translation
