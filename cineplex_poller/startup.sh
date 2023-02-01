#!/bin/sh

# aquired from https://docs.docker.com/compose/startup-order/
set -e -o xtrace

apk update && apk add gcc

apk update && apk add musl-dev

apk update && apk add alpine-conf
setup-timezone -z Canada/Pacific

pip install --no-cache-dir -r requirements.txt

python  -u cineplex_poller.py
