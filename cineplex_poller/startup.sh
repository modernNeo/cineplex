#!/bin/ash

apk update && apk add gcc

apk update && apk add musl-dev

apk update && apk add alpine-conf
setup-timezone -z Canada/Pacific

pip install --no-cache-dir -r requirements.txt

python cineplex_poller.py