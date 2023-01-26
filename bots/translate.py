import io
import os

from googletrans import Translator as GT
import cv2 as cv

from google.api_core.exceptions import AlreadyExists
from google.cloud import translate_v3beta1 as translate
from google.cloud import vision
from helpers import url2img

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = os.getenv("GCLOUD_PROJECT")

class Translator:
    def __init__(self):
        self.trans = translate.TranslationServiceClient()
        self.vision = vision.ImageAnnotatorClient()
    
    # def preprocess_image(self, img):
    #     img = cv.medianBlur(img, 1)
    #     grey = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    #     grey = cv.fastNlMeansDenoising(grey,)
    #     res = cv.adaptiveThreshold(grey, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
    #     cv.imwrite("threshed.png", res)

    #     return res

    def translate_image(self, *, path = None, url = None):
        if (path is not None):
            with io.open(path, "rb") as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
        else:
            image = vision.Image()
            image.source.image_uri = url

        response = self.vision.text_detection(image=image)
        text = response.full_text_annotation.text
        print("Detected text: {}".format(text))

        return self.translate_text(text)
    
    def create_glossary(self, glossary_name, glossary_uri):

        # Designates the data center location that you want to use
        location = "us-central1"

        # Set glossary resource name
        name = self.trans.glossary_path(gcloud_id, location, glossary_name)

        # Set language codes
        language_codes_set = translate.Glossary.LanguageCodesSet(
            language_codes=["en", "th"]
        )

        gcs_source = translate.GcsSource(input_uri=glossary_uri)

        input_config = translate.GlossaryInputConfig(gcs_source=gcs_source)

        # Set glossary resource information
        glossary = translate.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )

        parent = f"projects/{gcloud_id}/locations/{location}"

        # Create glossary resource
        # Handle exception for case in which a glossary
        #  with glossary_name already exists
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
    
    # def translate_image(self, *, url = None, image = None):
    #     if url != None:
    #         img = self.url2img(url)

    #     else:
    #         img = image

    #     factor = int(2000/img.shape[0])
    #     img =cv.resize(img, None, fx=factor, fy=factor, interpolation=cv.INTER_CUBIC)
 
    #     clean = self.preprocess_image(img)
        
    #     custom_config = r'--psm 11'
    #     result = pts.image_to_string(clean, lang='eng+tha', config=custom_config).replace(' ', '')
    #     d = pts.image_to_data(clean, lang='eng+tha', output_type=pts.Output.DICT, config=custom_config)
    #     text = ""
    #     index = 0
    #     n_boxes = len(d['text'])
    #     for i in range(n_boxes):
    #         if (d['text'][i] != '') and (int(d['conf'][i]) > 90):
    #             text += result[index]
    #             index += 1

    #     # rect = np.zeros(img.shape, dtype=np.uint8)
    #     # res = cv.addWeighted(img, 0.2, rect, 0.8, 1.0)
    #     text = text.replace(' ', '')
    #     print(text)
    #     print("-----------------------")
    #     text = self.translate_text(text)
    #     print(text)

    #     # img = cv.putText(img, text, (0, 0), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
    #     # cv.imwrite("translated.png", res)

    #     return text

    def translate_text(self, text, glossary_name):

        # Designates the data center location that you want to use
        location = "us-central1"

        glossary = self.trans.glossary_path(gcloud_id, location, glossary_name)

        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

        parent = f"projects/{gcloud_id}/locations/{location}"

        result = self.trans.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": "th",
                "target_language_code": "en",
                "glossary_config": glossary_config,
            }
        )

        # Extract translated text from API response
        return result.glossary_translations[0].translated_text

    # def translate_text(self, text):
    #     return self.trans.translate(text, src='th', dst='en').text

    
def main():
    trans = Translator()

    # img = cv.imread(, cv.IMREAD_COLOR)
    trans.translate_image(path="bots/test2.jpeg")

if __name__ == "__main__":
    main()