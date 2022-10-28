FROM python:3.9.13-alpine
RUN apk update && apk add alpine-conf
RUN setup-timezone -z Canada/Pacific

ENV SECRET_KEY=$SECRET_KEY
ENV HTTP_HOST=$HTTP_HOST
ENV WEBSITE_DATABASE_PATH=$WEBSITE_DATABASE_PATH

#EXPOSE 8000

WORKDIR /src

COPY cineplex_website/cineplex cineplex
COPY cineplex_website/cineplex_website cineplex_website
COPY cineplex_website/manage.py manage.py
COPY cineplex_website/startup.sh startup.sh
COPY cineplex_website/dockerized_requirements.txt requirements.txt
COPY cineplex_dockerized.env cineplex_dockerized.env


CMD ["./startup.sh"]

#CMD ["sh"]
