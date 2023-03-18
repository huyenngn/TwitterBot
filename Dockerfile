FROM python:3.10-slim-bullseye

WORKDIR /usr/app
COPY . .
RUN pip3 install --upgrade pip -r requirements.txt
CMD ["python3", "main.py"]
