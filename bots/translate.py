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

def cleanText(s):
    if len(s) < 5:
        return s
    if (s[0] == s[1] == s[2] == s[3] == s[4]) :
        return cleanText(s[1:])
    
    return s[0]+cleanText(s[1:])
 
class ContentTranslator:
    def __init__(self):
        self.vision = vision.ImageAnnotatorClient()
        self.small = ImageFont.truetype("NotoSerif-Regular.ttf", 10)
        self.medium = ImageFont.truetype("NotoSerif-Regular.ttf", 20)
        self.large = ImageFont.truetype("NotoSerif-Regular.ttf", 30)
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
                    draw.polygon(poly, fill=(255,255,255))
                    p = []
                    for word in paragraph.words:
                        w = []
                        for symbol in word.symbols:
                            w.append(symbol.text)
                        p.append("".join(w))
                    text = " ".join(p)
                    text = self.translate_text(text)

                    text_height = max([abs(poly[0][1]-poly[1][1]), abs(poly[0][1]-poly[2][1])])
                    print(text_height)
                    font = self.small if text_height < 40 else (self.medium if text_height < 60 else self.large)
                    draw.text(poly[0],text,(0,0,0),font=font)
        pil_image.show()

        return img2byte(pil_image)
    
    def translate_text(self, text):
        if not text:
            return ""
        
        translation = text
        for th, en in translation_settings["glossary"].items():
            translation = translation.replace(th, en)

        translation = self.google.translate(cleanText(translation), src=translation_settings["src"], dst=translation_settings["dst"]).text
        for src, dst in translation_settings["corrections"].items():
            translation = translation.replace(src, dst)

        return translation

    
def main():
    trans = ContentTranslator()
    text = "ไม่ส่งรูปให้นุบ้างเลยยยยยยยย งอน (ง้อด้วย)🥹"
    print(trans.translate_text(text))
    # trans.translate_image("https://pbs.twimg.com/media/FkA-R4gUoAA1Cap?format=jpg&name=small")

if __name__ == "__main__":
    main()