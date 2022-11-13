FROM python:3.9.13

ARG ENVIRONMENT=default

ENV PYTHONUNBUFFERED 1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN set -x \
  && buildDeps=" \
  build-essential \
  libpq-dev \
  unzip \
  " \
  && runDeps=" \
  git \
  " \
  && apt-get update \
  && apt-get install -y --no-install-recommends $buildDeps \
  && apt-get install -y --no-install-recommends $runDeps \
  && pip install -r /tmp/requirements.txt \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY . .