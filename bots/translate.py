from io import BytesIO
import os
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
from google.api_core.exceptions import AlreadyExists
from google.cloud import translate_v3beta1 as translate
from google.cloud import vision
import base64
import requests

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = "twitterbot-376108"

class Content_Translator:
    def __init__(self):
        self.gt = Translator()
        self.trans = translate.TranslationServiceClient()
        self.vision = vision.ImageAnnotatorClient()
        self.location = "us-central1"
        self.font = ImageFont.truetype("NotoSerif-Regular.ttf", 15)

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

                    draw.text(poly[0],text,(0,0,255),font=self.font)
        buff = BytesIO()
        pil_image.save(buff, format="JPEG")
        res = base64.b64encode(buff.getvalue())
        return buff.getvalue()
    
    def create_glossary(self, glossary_name, glossary_uri):
        # Set glossary resource name
        name = self.trans.glossary_path(gcloud_id, self.location, glossary_name)

        # Set language codes
        language_codes_set = translate.Glossary.LanguageCodesSet(
            language_codes=["th", "en"]
        )

        gcs_source = translate.GcsSource(input_uri=glossary_uri)

        input_config = translate.GlossaryInputConfig(gcs_source=gcs_source)

        # Set glossary resource information
        glossary = translate.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )

        parent = f"projects/{gcloud_id}/locations/{self.location}"

        # Create glossary resource
        try:
            operation = self.trans.create_glossary(parent=parent, glossary=glossary)
            operation.result(timeout=90)
            print("Created glossary " + glossary_name + ".")
        except AlreadyExists:
            print(
                "The glossary "
                + glossary_name
                + " already exists. No new glossary was created."
            )
    def delete_glossary(self, glossary_name):
        name = self.trans.glossary_path(gcloud_id, self.location, glossary_name)

        operation = self.trans.delete_glossary(name=name)
        result = operation.result(180)
        print("Deleted: {}".format(result.name))
    
    def translate_text(self, text):
        if not text:
            return ""

        glossary = self.trans.glossary_path(gcloud_id, self.location, "glossary")

        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

        parent = f"projects/{gcloud_id}/locations/{self.location}"

        result = self.trans.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": "th",
                "target_language_code": "en",
                "glossary_config": glossary_config,
            }
        )

        return result.glossary_translations[0].translated_text

    def google_translate(self, text):
        return self.gt(text, src='th', dst='en').text

    
def main():
    trans = Translator()
    # trans.delete_glossary("glossary")
    # trans.create_glossary("glossary", "gs://twitterbot-bucket/glossary.csv")
    trans.translate_image("https://pbs.twimg.com/media/Fj3wjKiVEAE-wRq?format=jpg&name=900x900")

if __name__ == "__main__":
    main()