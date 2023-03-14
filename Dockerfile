FROM ubuntu:22.04
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 python3-pip
WORKDIR /usr/app
COPY . .
RUN pip3 install -r requirements.txt
RUN python3 -m playwright install
CMD ["python3", "main.py"]
