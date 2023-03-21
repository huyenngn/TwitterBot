from io import BytesIO
import os
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision
from google.cloud import translate
from google.api_core.exceptions import AlreadyExists
import requests

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = os.getenv("GCLOUD_ID")

class Translator:
    def __init__(self, src, dst, glossary={}, corrections={}):
        self.vision = vision.ImageAnnotatorClient()
        self.google = translate.TranslationServiceClient()
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

        location = "us-central1"

        glossary = self.google.glossary_path(gcloud_id, location, "glossary")

        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

        parent = f"projects/{gcloud_id}/locations/{location}"

        response = self.google.translate_text(
            request={
                "parent": parent,
                "contents": [t],
                "mime_type": "text/plain",
                "source_language_code": self.src,
                "target_language_code": self.dst,
                "glossary_config": glossary_config,
            }
        )

        translation = response.glossary_translations[0].translated_text

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
                    para = "".join(p)
                    text = self.translate_text(para)

                    if para.lower() == text.lower():
                        continue

                    poly = []
                    for vertex in paragraph.bounding_box.vertices:
                        v = (vertex.x, vertex.y)
                        poly.append(v)
                    draw.polygon(poly, fill=(255, 255, 255))

                    poly_width = abs(poly[0][0] - poly[2][0])
                    poly_height = abs(poly[0][1] - poly[2][1])

                    p = text.split()
                    number_of_lines = int(1 + (len(p)/10)*(poly_height/poly_width))
                    line_size = min(10, int(len(p)/number_of_lines))

                    temp = []
                    for i in range(0, number_of_lines):
                        start = i * line_size
                        end = (i+1) * line_size
                        temp.append(" ".join(p[start:end]))
                    temp.append(" ".join(p[end:]))
                    text = "\n".join(temp)

                    fontsize = int(pil_image.size[0]/70)
                    font = ImageFont.truetype("src/modules/NotoSerif-Regular.ttf", fontsize)
                    bbox = draw.multiline_textbbox(poly[0], text, font=font)
                    while abs(bbox[0] - bbox[2]) < poly_width and abs(bbox[1] - bbox[3]) < poly_height:
                        fontsize += 1
                        font = ImageFont.truetype("src/modules/NotoSerif-Regular.ttf", fontsize)
                        bbox = draw.multiline_textbbox(poly[0], text, font=font)
                    print(fontsize)
                    draw.rectangle(bbox, fill=(255, 255, 255))
                    draw.multiline_text(poly[0], text, (0, 0, 0), font=font)
        
        buff = BytesIO()
        pil_image.save(buff, format="JPEG")
        return buff.getvalue()

def create_glossary ():

        client = translate.TranslationServiceClient()
        location = "us-central1"

        name = client.glossary_path(gcloud_id, location, "glossary")

        language_codes_set = translate.Glossary.LanguageCodesSet(
            language_codes=["th", "en"]
        )

        gcs_source = translate.GcsSource(input_uri="gs://freenbeckybot/glossary.csv")

        input_config = translate.GlossaryInputConfig(gcs_source=gcs_source)

        glossary = translate.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )

        parent = f"projects/{gcloud_id}/locations/{location}"

        try:
            operation = client.create_glossary(parent=parent, glossary=glossary)
            operation.result(timeout=90)
            print("Created glossary.")
        except AlreadyExists:
            operation = client.delete_glossary(name=name)
            result = operation.result(180)
            print("Deleted: {}".format(result.name))
            create_glossary()

if __name__ == "__main__":
    create_glossary()
    tl = Translator("th", "en")
    text = "วันนี้สนุกมั้ยค่าาา เล่าให้นุฟังหน่อยย🫶🏻 ขอบคุณที่มาดูนะคะ🫠🥹🧸💖 #AurameXBecky"
    print(tl.translate_text(text))