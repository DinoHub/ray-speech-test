# docker build -f head.Dockerfile -t ray/head:v2.4.0 .

FROM ubuntu:22.04

ARG RAY_SERVE_VERSION=2.4.0
ARG PYTHON_VERSION=3.10

ENV DEBIAN_FRONTEND=noninteractive

ENV cwd="/home/"
WORKDIR $cwd

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV TZ=Asia/Singapore
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get -y update && \
    apt-get -y upgrade && \
    apt -y update && \
    apt-get install --no-install-recommends -y \
        software-properties-common \
        build-essential \
        wget \
        curl \
        gpg-agent \
        podman && \
    apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && apt-get -y autoremove && \
    rm -rf /var/cache/apt/archives/

# Install and set the chosen python version as the default python
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get install --no-install-recommends -y python$PYTHON_VERSION-dev python$PYTHON_VERSION-venv python3-pip && \
    apt -y update && \
    python$PYTHON_VERSION -m venv /venv
ENV PATH=/venv/bin:$PATH

# install nvidia docker
RUN distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && \
    curl -sS https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor | tee /etc/apt/trusted.gpg.d/nvidia-container-toolkit-keyring.gpg && \
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list && \
    apt-get -y update && \
    apt-get install --no-install-recommends -y nvidia-docker2 && \
    apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && apt-get -y autoremove && \
    rm -rf /var/cache/apt/archives/

COPY ./requirements.txt requirements.txt

RUN python3 -m pip install --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir ray[serve]==$RAY_SERVE_VERSION && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm requirements.txt