FROM python:3.10-slim-bullseye

COPY bots/main.py /bots/
COPY bots/twitter.py /bots/
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /bots
CMD ["python3", "main.py"]