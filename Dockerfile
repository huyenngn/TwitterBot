FROM ubuntu:22.04
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 python3-pip gstreamer1.0-libav libnss3-tools libatk-bridge2.0-0 libcups2-dev libxkbcommon-x11-0 libxcomposite-dev libxrandr2 libgbm-dev libgtk-3-0
WORKDIR /usr/app
COPY . .
RUN pip3 install -r requirements.txt
RUN python3 -m playwright install
CMD ["python3", "main.py"]
