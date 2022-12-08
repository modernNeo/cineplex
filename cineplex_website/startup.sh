#!/bin/ash

apk update && apk add gcc
apk update && apk add musl-dev

apk add postgresql

apk update && apk add alpine-conf
setup-timezone -z Canada/Pacific

pip install --no-cache-dir -r requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8001