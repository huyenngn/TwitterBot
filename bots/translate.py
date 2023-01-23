import cv2 as cv
import numpy as np
import requests
from googletrans import Translator as GT
import pytesseract as pts

class Translator:
    def __init__(self):
        self.trans = GT()

    def url2img(self, url):
        response = requests.get(url)
        img = np.asarray(bytearray(response.content), dtype="uint8")
        img = cv.imdecode(img, cv.IMREAD_COLOR)

        return img
    
    def preprocess_image(self, img):
        img = cv.medianBlur(img, 1)
        grey = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        grey = cv.fastNlMeansDenoising(grey,)
        res = cv.adaptiveThreshold(grey, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
        cv.imwrite("threshed.png", res)

        return res
    
    def translate_image(self, *, url = None, image = None):
        if url != None:
            img = self.url2img(url)
        else:
            img = image
        custom_config = r'-l tha --psm 6'
        d = pts.image_to_data(img, output_type=pts.Output.DICT, config=custom_config)
        n_boxes = len(d['text'])
        for i in range(n_boxes):
            if int(d['conf'][i]) > 60:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

                sub_img = img[y:y+h, x:x+w]
                rect = np.zeros(sub_img.shape, dtype=np.uint8)
                res = cv.addWeighted(sub_img, 0.5, rect, 0.5, 1.0)
                img[y:y+h, x:x+w] = res

                text = self.translate_text(d['text'][i])
                img = cv.putText(img, text, (x+w, y+h), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

        cv.imwrite("translated.png", img)

        return img

    def translate_text(self, text):
        return self.trans.translate(text, src='th', dst='en').text

    
def main():
    trans = Translator()
    # img = trans.url2img("https://pbs.twimg.com/media/Fj3wjKiVEAE-wRq?format=jpg&name=900x900")
    img = cv.imread("bots/test.jpeg")
    trans.translate_image(image=img)

    if cv.waitKey() & 0xff == 27: quit()

if __name__ == "__main__":
    main()