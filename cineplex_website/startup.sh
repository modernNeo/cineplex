#!/bin/ash

apk update && apk add gcc
apk update && apk add musl-dev

pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir -r poll_cineplex/dockerized_requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000