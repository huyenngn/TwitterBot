FROM python:3.10-slim-bullseye

WORKDIR /usr/app
COPY . .
RUN pip3 install --upgrade pip -r requirements.txt
RUN python3 -m playwright install
RUN npx playwright install-deps
CMD ["python3", "main.py"]
