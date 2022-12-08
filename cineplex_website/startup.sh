#!/bin/ash

apk update && apk add gcc
apk update && apk add musl-dev

apk update && apk add alpine-conf
setup-timezone -z Canada/Pacific

pip install --no-cache-dir -r requirements.txt

# this is here cause the user has the option of manually running a poll via the website
pip install --no-cache-dir -r cineplex_poller/requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000