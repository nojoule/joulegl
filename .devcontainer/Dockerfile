FROM ubuntu:jammy

# install python 3.11
RUN apt-get update && apt-get install -y python3.11 python3-pip mesa-utils xvfb libsm6 libxext6 libgl1-mesa-dev libosmesa6-dev

COPY requirements-dev.txt .

RUN pip install -r requirements-dev.txt
