FROM python:3.9.13-alpine

WORKDIR /src/app/cineplex
COPY cineplex_website/cineplex/models.py models.py

WORKDIR /src/app
COPY cineplex_poller/settings.py settings.py
COPY cineplex_poller/dockerized_requirements.txt requirements.txt
COPY cineplex_poller/cineplex_poller.py cineplex_poller.py
COPY CI/wait-for-postgres.sh wait-for-postgres.sh
COPY cineplex_poller/startup.sh startup.sh

RUN apk add postgresql

CMD ["./wait-for-postgres.sh", "./startup.sh"]

#CMD ["sh"]
