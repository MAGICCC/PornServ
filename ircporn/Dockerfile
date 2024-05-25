FROM alpine:3.20

LABEL maintainer "MAGICCC <magic@kthx.at>"

ARG PIP_BREAK_SYSTEM_PACKAGES=1 
COPY requirements.txt /tmp/
RUN apk upgrade --no-cache \
    && apk add --update --no-cache \
    tzdata \
    python3 \
    py-pip \
    && pip3 install --upgrade pip setuptools \
    && rm -r /root/.cache \
    && pip3 install --requirement /tmp/requirements.txt