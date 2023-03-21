FROM python:3.10-slim-bullseye

WORKDIR /usr/app
COPY requirements.txt .
RUN pip3 install --upgrade pip -r requirements.txt
COPY . .
CMD ["python3", "main.py"]
