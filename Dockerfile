FROM python:3.10-slim-bullseye

COPY bots/twitter.py /bots/
COPY bots/config.py /bots/
COPY bots/translate.py /bots/
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt
# RUN apt install libtesseract-dev tesseract-ocr tesseract-ocr-tha python3-opencv


WORKDIR /bots
CMD ["python3", "twitter.py"]