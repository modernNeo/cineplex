import datetime
import json
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from twilio.rest import Client

from cineplex_website.models import DateToQuery, Movie, Showing


class Command(BaseCommand):
    help = "nag any officers who have not entered their info"

    def handle(self, *args, **options):
        location_id = 1412
        headers = {
            "Ocp-Apim-Subscription-Key": os.environ['CINEPLEX_SUBSCRIPTION_KEY']
        }
        # Showing.objects.all().delete()
        existing_shows = {
            showing.id: showing
            for showing in Showing.objects.all().filter(date__gte=datetime.datetime.now())
        }
        new_shows_with_cc = []
        for date_to_query in DateToQuery.objects.all():
            if datetime.datetime.now().date() <= date_to_query.date:
                for movie_and_date_intersection in date_to_query.movieanddateintersection_set.all():
                    film_id = movie_and_date_intersection.movie.filmId
                    response = requests.request(
                        "GET",
                        (
                            f"https://apis.cineplex.com/prod/cpx/theatrical/api/v1/showtimes?language=en&"
                            f"locationId={location_id}&date={date_to_query.get_date}&filmId={film_id}"
                        ),
                        headers=headers, data={}
                    )
                    for showing_types in (json.loads(response.text))[0]['dates'][0]['movies'][0]['experiences']:
                        movie = Movie.objects.get_or_create(filmId=film_id)[0]
                        for session in showing_types['sessions']:
                            showtime_date_and_time = datetime.datetime.strptime(
                                session['showStartDateTime'],
                                "%Y-%m-%dT%H:%M:%S"
                            )
                            last_row = None
                            seating = BeautifulSoup(
                                urlopen(session['seatMapUrl']).read(),
                                features="html.parser"
                            )
                            for script in seating(["script"]):
                                if "SeatMapData" in script.next:
                                    x = json.loads(re.search('({.+})', script.next).group(0).replace("'", '"'))
                                    rows = x['SeatMapData']['Rows']
                                    last_row = rows[len(rows) - 1]['RowLabel']
                            showing, new = Showing.objects.get_or_create(
                                movie=movie, date=showtime_date_and_time.date(), time=showtime_date_and_time.time(),
                                showing_type=" ".join(showing_types['experienceTypes']),
                                auditorium=session['auditorium'],
                                seatMapUrl=session['seatMapUrl'], last_row=last_row,
                                payment_url=session['ticketingUrl']
                            )
                            if new:
                                showing.seatsRemaining = session['seatsRemaining']
                                showing.cc_enabled = showing_types['isCcEnabled']
                                showing.ds_enabled = showing_types['isDsEnabled']
                                if showing_types['isCcEnabled'] or showing_types['isDsEnabled']:
                                    new_shows_with_cc.append(showing)
                                showing.save()
                            else:
                                if not existing_shows[showing.id].visible:
                                    showing._visible = True
                                del existing_shows[showing.id]
                                showing._seatsRemaining = session['seatsRemaining']
                                showing._cc_enabled = showing_types['isCcEnabled']
                                showing._ds_enabled = showing_types['isDsEnabled']
                                if (
                                        (showing_types['isCcEnabled'] and showing_types[
                                            'isCcEnabled'] != showing.cc_enabled) or
                                        (showing_types['isDsEnabled'] and showing_types[
                                            'isDsEnabled'] != showing.ds_enabled)
                                ):
                                    new_shows_with_cc.append(showing)
                                showing.save()
        for existing_show in existing_shows.values():
            existing_show._visible = False
            existing_show.save()
        new_shows_with_cc = "\n".join(new_shows_with_cc)
        send_alerts(new_shows_with_cc)


def send_alerts(showings: str):
    send_email(showings)
    send_sms()
    print(f"all enabled alerts sent to me")


def send_sms(movie_name: str = None, movie_link: str = None):
    # https://www.fullstackpython.com/blog/send-sms-text-messages-python.html
    body = f"{movie_name} is now available: {movie_link}"
    # the following line needs your Twilio Account SID and Auth Token
    client = Client(f"{os.environ['TWILIO_ACCOUNT_SID']}", f"{os.environ['TWILIO_AUTH_TOKEN']}")

    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to=f"{os.environ['PHONE_NUMBER']}",
                           from_=f"{os.environ['TWILIO_VIRTUAL_NUMBER']}",
                           body=body)
    print(f"text sent to {os.environ['PHONE_NUMBER']} for new CC movies")


def send_email(showings: str = None):
    from_person_name = 'Cineplex-CC-Showings'
    from_person_email = 'bestbuy.steelbooks@gmail.com'
    password = f"{os.environ['BESTBUY_STEELBOOKS_PASSWORD']}"
    to_person_email = os.environ['TO_EMAIL']
    subject = f'More tickets available in CC for movies'
    body = showings

    print("Setting up MIMEMultipart object")
    msg = MIMEMultipart()
    msg['From'] = from_person_name + " <" + from_person_email + ">"
    msg['To'] = " <" + to_person_email + ">"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    print("Connecting to smtp.gmail.com:587")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.connect("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    print("Logging into your gmail")
    server.login(from_person_email, password)
    print("Sending email...")
    server.send_message(from_addr=from_person_email, to_addrs=to_person_email, msg=msg)
    server.close()
    print(f"email sent to {os.environ['TO_EMAIL']} for new CC movies")
