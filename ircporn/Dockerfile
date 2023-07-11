FROM alpine:3.18

LABEL maintainer "MAGICCC <magic@kthx.at>"


COPY requirements.txt /tmp/
RUN apk upgrade --no-cache \
    && apk add --update --no-cache \
    tzdata \
    python3 \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi \
    && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi \
    && rm -r /root/.cache \
    && pip3 install --requirement /tmp/requirements.txt
