FROM python:3.10-slim-bullseye

COPY bots/instagram_updates.py /bots/
COPY bots/instagram_updates.py /bots/
COPY twitterbot-376108-554b24ce03a2.json /bots/modules
COPY bots/modules/twitter.py /bots/modules
COPY bots/modules/translate.py /bots/modules
COPY bots/modules/thai2eng.py /bots/modules
COPY bots/modules/instagram.py /bots/modules
COPY bots/modules/instagram.py /bots/modules
COPY bots/modules/helpers.py /bots/modules
COPY bots/modules/NotoSerif-Regular.ttf /bots/modules
COPY test.py /bots/
COPY requirements.txt /tmp
RUN pip3 install --upgrade pip -r /tmp/requirements.txt

WORKDIR /bots
CMD ["python3", "test.py"]