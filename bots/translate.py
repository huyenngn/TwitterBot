# import cv2 as cv
import numpy as np
import requests
from googletrans import Translator as GT
# import pytesseract as pts

class Translator:
    def __init__(self):
        self.trans = GT()

    # def url2img(self, url):
    #     response = requests.get(url)
    #     img = np.asarray(bytearray(response.content), dtype="uint8")
    #     img = cv.imdecode(img, cv.IMREAD_COLOR)

    #     return img
    
    # def preprocess_image(self, img):
    #     img = cv.medianBlur(img, 1)
    #     grey = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    #     grey = cv.fastNlMeansDenoising(grey,)
    #     res = cv.adaptiveThreshold(grey, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
    #     cv.imwrite("threshed.png", res)

    #     return res
    
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

    def translate_text(self, text):
        return self.trans.translate(text, src='th', dst='en').text

    
def main():
    trans = Translator()
    # img = cv.imread("bots/test2.jpeg", cv.IMREAD_COLOR)
    # trans.translate_image(image=img)

if __name__ == "__main__":
    main()