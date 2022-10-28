FROM python:3.9.13-alpine
RUN apk update && apk add alpine-conf
RUN setup-timezone -z Canada/Pacific

ENV BOT_DATABASE_PATH=$BOT_DATABASE_PATH

WORKDIR /src/cineplex
COPY cineplex_website/cineplex/models.py models.py

WORKDIR /src
COPY cineplex_poller/settings.py settings.py
COPY cineplex_poller/dockerized_requirements.txt requirements.txt
COPY cineplex_dockerized.env cineplex_dockerized.env
COPY cineplex_poller/cineplex_poller.py cineplex_poller.py

RUN apk update && apk add gcc

RUN apk update && apk add musl-dev

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "cineplex_poller.py"]

#CMD ["sh"]

#BASE_DIR=/
#DATABASES[default][NAME]=/sqlite_db/db.sqlite3
