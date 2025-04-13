FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    curl \
    sudo \
    gcc \
    g++ \
    libssl-dev \
    wget \
    patchelf \
    ccache \
    scons \
    && pip install --upgrade pip

RUN pip install nuitka colorama requests

WORKDIR /app

ENV CC="ccache gcc"

CMD ["bash"]
