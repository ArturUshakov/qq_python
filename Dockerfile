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
