FROM ubuntu:22.04
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 pip3 \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /usr/app
COPY . .
RUN pip3 install --upgrade pip -r requirements.txt
RUN python3 -m playwright install
RUN npx playwright install-deps
CMD ["python3", "main.py"]
