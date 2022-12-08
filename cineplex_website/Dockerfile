FROM python:3.9.13-alpine

EXPOSE 8000

EXPOSE 5432

WORKDIR /src/app

COPY cineplex_website/cineplex cineplex

# this is here cause the user has the option of manually running a poll via the website
WORKDIR /src/app/cineplex_poller
COPY cineplex_poller/cineplex_poller.py cineplex_poller.py
COPY cineplex_poller/dockerized_requirements.txt requirements.txt

WORKDIR /src/app
COPY cineplex_website/cineplex_website cineplex_website
COPY cineplex_website/manage.py manage.py
COPY cineplex_website/startup.sh startup.sh
COPY cineplex_website/dockerized_requirements.txt requirements.txt
COPY cineplex_dockerized.env cineplex_dockerized.env
COPY CI/wait-for-postgres.sh wait-for-postgres.sh

RUN apk add postgresql

CMD ["./wait-for-postgres.sh", "./startup.sh"]

#CMD ["sh"]
