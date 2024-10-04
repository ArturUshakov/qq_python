# docker build -t nuitka_project .
# docker run --rm -v /home/artur/qq_test:/app/output -it nuitka_project /bin/bash
# python3.8 -m nuitka --onefile --follow-imports --output-dir=output main.py

FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-distutils \
    gcc \
    g++ \
    clang \
    build-essential \
    patchelf \
    zlib1g-dev \
    curl \
    && apt-get clean

RUN pip3 install --upgrade pip \
    && pip3 install colorama requests tqdm nuitka

WORKDIR /app

COPY . .
