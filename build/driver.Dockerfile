# docker build -f driver.Dockerfile -t ray/driver:v2.4.0 .

ARG PYTHON_VERSION=3.10

FROM python:$PYTHON_VERSION-slim

ARG RAY_SERVE_VERSION=2.4.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

WORKDIR /ray_driver

RUN python3 -m pip install --upgrade pip setuptools wheel && \
    pip3 install --no-cache-dir ray[serve]==$RAY_SERVE_VERSION && \
    pip3 install --no-cache-dir shapely==2.0.1

COPY . /ray_driver/

CMD bash run.sh