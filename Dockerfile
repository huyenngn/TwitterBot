FROM python:3.10-slim-bullseye

RUN pip3 install --upgrade pip -r requirements.txt
WORKDIR /usr/app
COPY . .
CMD ["python3", "main.py"]
