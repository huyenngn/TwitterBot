FROM python:3.10-slim-bullseye

COPY test.py /src/
COPY bots/instagram_updates.py /src/bots
COPY bots/instagram_updates.py /src/bots
COPY twitterbot-376108-554b24ce03a2.json /src/bots/modules/
COPY bots/modules/twitter.py /src/bots/modules/
COPY bots/modules/translate.py /src/bots/modules/
COPY bots/modules/thai2eng.py /src/bots/modules/
COPY bots/modules/instagram.py /src/bots/modules/
COPY bots/modules/instagram.py /src/bots/modules/
COPY bots/modules/helpers.py /src/bots/modules/
COPY bots/modules/NotoSerif-Regular.ttf /src/bots/modules/
COPY requirements.txt /tmp
RUN pip3 install --upgrade pip -r /tmp/requirements.txt

WORKDIR /src
CMD ["python3", "test.py"]