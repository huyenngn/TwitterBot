from io import BytesIO
import logging
import os
from modules.util import img2byte
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator as GT
from google.cloud import vision
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = os.getenv("GCLOUD_ID")

translation_settings = {
    # language settings
    "src": "th",
    "dst": "en",
    # replacements applied before translating
    "glossary": {
        "อะะ": " ahh",
        "ง้อ": "reconcile",
        "งอน": "sulking",
        "คนรัก": "คนที่รัก",  # people to love
        "มามี้": "Mami",
        "ยัก": "รัก",  # yak
        "ฟรีนกี้": "Freenky",
        "ฟรีน": "Freen",
        "สาม": "แซม",  # Sam
        "นุคน": "หนู",  # Nu -> Sandra
        "นุ": "หนู",
        "หนู": "แซนดร้า",
        "น้องพุง": "Nong Belly",
        "น้อง": "Nong",
        "พี่": "Phi",
        "ยัง": "",  # still/yet
        "อะ": "",  # a
    },
    # replacements applied after translating
    "corrections": {
        "Sandra": "Nu",
        "Beck ": "Bec",
        "I am": "",
        "I'm ": "",
        "I ": "",
        " me ": " me/you ",
        " me.": " me/you.",
        "boyfriend": "girlfriend",
    },
}


class Translator:
    def __init__(self):
        self.vision = vision.ImageAnnotatorClient()
        self.google = GT()
        self.glossary = translation_settings["glossary"]
        self.corrections = translation_settings["corrections"]
        self.src = translation_settings["src"]
        self.dst = translation_settings["dst"]

    def translate_text(self, text):
        if not text:
            return ""

        detected = self.google.detect(text)
        if detected.lang == "en":
            if detected.confidence > 0.2:
                return ""
            lang = self.src
        else:
            lang = detected.lang

        translation = text
        for src, dst in self.glossary.items():
            translation = translation.replace(src, dst)

        translation = self.google.translate(
            translation,
            src=lang,
            dst=self.dst,
        ).text

        for src, dst in self.corrections.items():
            translation = translation.replace(src, dst)

        return translation

    def translate_image(self, url):
        raw_image = requests.get(url).content

        pil_image = Image.open(BytesIO(raw_image))
        draw = ImageDraw.Draw(pil_image)

        image = vision.Image(content=raw_image)
        data = self.vision.document_text_detection(image=image)

        for page in data.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    p = []
                    for word in paragraph.words:
                        w = []
                        for symbol in word.symbols:
                            w.append(symbol.text)
                        p.append("".join(w))
                    text = " ".join(p)
                    text = self.translate_text(text)

                    if not text:
                        continue

                    text = text.replace(", ", ",\n")
                    text = text.replace(". ", ".\n")

                    poly = []
                    for vertex in paragraph.bounding_box.vertices:
                        p = (vertex.x, vertex.y)
                        poly.append(p)
                    draw.polygon(poly, fill=(255, 255, 255))

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
