from io import BytesIO
import logging
import os
from bots.modules.util import img2byte
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator as GT
from google.cloud import vision
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = os.getenv("GCLOUD_ID")


class Translator:
    def __init__(self, src, dst, glossary={}, corrections={}):
        self.vision = vision.ImageAnnotatorClient()
        self.google = GT()
        self.glossary = glossary
        self.corrections = corrections
        self.src = src
        self.dst = dst

    def translate_text(self, text):
        if not text:
            return ""

        t = text
        for src, dst in self.glossary.items():
            t = t.replace(src, dst)

        translation = self.google.translate(t, src=self.src, dst=self.dst).text

        if translation != t:
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
                    para = " ".join(p)
                    text = self.translate_text(para)

                    if para == text:
                        continue

                    poly = []
                    for vertex in paragraph.bounding_box.vertices:
                        p = (vertex.x, vertex.y)
                        poly.append(p)
                    draw.polygon(poly, fill=(255, 255, 255))

                    poly_width = abs(poly[0][0] - poly[2][0])
                    poly_height = abs(poly[0][1] - poly[2][1])

                    para = text.split(" ")
                    number_of_lines = 1 + int((len(para)/2)*(poly_height/poly_width))
                    print(number_of_lines)
                    if number_of_lines > 1:
                        line_size = int(len(para)/number_of_lines)
                        temp = []
                        for i in range(1, number_of_lines):
                            start = (i-1) * line_size
                            end = i * line_size
                            temp.append(" ".join(para[start:end]))
                        temp.append(" ".join(para[end:]))
                        text = "\n".join(temp)

                    fontsize = 13
                    font = ImageFont.truetype("bots/modules/NotoSerif-Regular.ttf", fontsize)
                    bbox = draw.multiline_textbbox(poly[0], text, font=font)
                    while abs(bbox[0] - bbox[2]) < poly_width and (bbox[1] - bbox[3]) < poly_height:
                        fontsize += 1
                        font = ImageFont.truetype("bots/modules/NotoSerif-Regular.ttf", fontsize)
                        bbox = draw.multiline_textbbox(poly[0], text, font=font)

                    draw.rectangle(bbox, fill=(255, 255, 255))
                    draw.multiline_text(poly[0], text, (0, 0, 0), font=font)
        pil_image.show()

        return img2byte(pil_image)


def main():
    tl = Translator("th", "en")
    tl.translate_image("https://pbs.twimg.com/media/FO3yZeYVsAEfBJx?format=jpg&name=large")


if __name__ == "__main__":
    main()