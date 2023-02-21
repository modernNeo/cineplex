import datetime
import json
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep
from urllib.request import urlopen

import django
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from twilio.rest import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from cineplex.models import DateToQuery, Movie, Showing


def poll_which_cineplex_movies_are_available():
    headers = {
        "Ocp-Apim-Subscription-Key": os.environ['CINEPLEX_SUBSCRIPTION_KEY']
    }
    date = datetime.datetime.now().strftime("%Y/%m/%d - %-H:%M:%S")
    print(f"{date}-will start polling which movies are available")
    response = requests.request(
        "GET", f"https://apis.cineplex.com/prod/cpx/theatrical/api/v1/movies/bookable?language=en", headers=headers,
        data={}
    )
    print("got the list of movies that are available")
    response = (json.loads(response.text))
    movies = Movie.objects.all()
    for movie in response:
        print(f"parsing movie {movie}")
        if movies.filter(filmId=movie['id']) is None:
            if "shazam" in movie['name'].lower():
                send_email("Shazam movie tickets are out")
            Movie(filmId=movie['id'], name=movie['name']).save()
    print(f"{date}-finished updating the list of movies that are available")


def poll_cineplex_showings():
    date = datetime.datetime.now().strftime("%Y/%m/%d - %-H:%M:%S")
    location_id = 1412
    headers = {
        "Ocp-Apim-Subscription-Key": os.environ['CINEPLEX_SUBSCRIPTION_KEY']
    }
    existing_shows = {}
    max_retries = 5
    current_retries = 0
    db_is_ready = False
    while current_retries < max_retries and not db_is_ready:
        try:
            print(f"attempt {current_retries}/{max_retries}")
            current_retries += 1
            existing_shows = {
                showing.id: showing
                for showing in Showing.objects.all().filter(date__gt=datetime.datetime.now())
            }
            existing_shows.update({
                showing.id: showing
                for showing in
                Showing.objects.all().filter(date=datetime.datetime.now()).filter(time__gte=datetime.datetime.now())
            })
            db_is_ready = True
        except Exception as e:
            sleep(5)
            print(f"got error {e}")
    if not db_is_ready:
        raise Exception("shutting down cause the db won't get ready")
    print(f"{date}-starting poll")
    new_shows_with_cc = []
    current_time = datetime.datetime.now()
    for date_to_query in DateToQuery.objects.all():
        print(f"parsing {date_to_query.date}")
        if datetime.datetime.now().date() <= date_to_query.date:
            for movie_and_date_intersection in date_to_query.movieanddateintersection_set.all():
                print(f"parsing {movie_and_date_intersection.movie.name}")
                film_id = movie_and_date_intersection.movie.filmId
                response = requests.request(
                    "GET",
                    (
                        f"https://apis.cineplex.com/prod/cpx/theatrical/api/v1/showtimes?language=en&"
                        f"locationId={location_id}&date={date_to_query.get_front_end_date}&filmId={film_id}"
                    ),
                    headers=headers, data={}
                )
                for showing_types in (json.loads(response.text))[0]['dates'][0]['movies'][0]['experiences']:
                    movie = Movie.objects.get_or_create(filmId=film_id)[0]
                    for session in showing_types['sessions']:
                        exp_types = " ".join(showing_types['experienceTypes'])
                        print(f"{exp_types}-{session['showStartDateTime']}")
                        showtime_date_and_time = datetime.datetime.strptime(
                            session['showStartDateTime'],
                            "%Y-%m-%dT%H:%M:%S"
                        )
                        last_row = None
                        if session.get('isSoldOut', None) is not None and not session['isSoldOut']:
                            try:
                                seating = BeautifulSoup(
                                    urlopen(session['seatMapUrl']).read(),
                                    features="html.parser"
                                )
                                for script in seating(["script"]):
                                    if "SeatMapData" in script.next:
                                        x = json.loads(re.search('({.+})', script.next).group(0).replace("'", '"'))
                                        rows = x['SeatMapData']['Rows']
                                        last_row = rows[len(rows) - 1]['RowLabel']
                            except Exception as e:
                                print(e)
                        showing = Showing.objects.all().filter(payment_url=session['ticketingUrl']).first()
                        if showing is None:
                            showing = Showing(payment_url=session['ticketingUrl'])
                            showing.movie = movie
                            showing.date = showtime_date_and_time.date()
                            showing.time = showtime_date_and_time.time()
                            showing.showing_type = " ".join(showing_types['experienceTypes'])
                            showing.auditorium = session['auditorium']
                            showing.seatMapUrl = session['seatMapUrl']
                            showing.seatsRemaining = session['seatsRemaining']
                            showing.cc_enabled = showing_types['isCcEnabled']
                            showing.ds_enabled = showing_types['isDsEnabled']
                            showing.last_row = last_row
                            if showing_types['isCcEnabled'] or showing_types['isDsEnabled']:
                                new_shows_with_cc.append(f"{showing}")
                            showing.save()
                        else:
                            if current_time <= showtime_date_and_time:
                                if showing.id in existing_shows:
                                    if not existing_shows[showing.id].visible:
                                        showing._visible = True
                                    del existing_shows[showing.id]
                                else:
                                    showing.visible = True
                                    print(
                                        f"showing with id {showing.id} "
                                        f"could not be found in the dict of existing showings"
                                    )
                                showing._seatsRemaining = session['seatsRemaining']
                                showing._cc_enabled = showing_types['isCcEnabled']
                                showing._ds_enabled = showing_types['isDsEnabled']
                                showing._time = showtime_date_and_time.time()
                                showing._last_row = last_row
                                if (
                                    (showing_types['isCcEnabled'] and showing_types[
                                        'isCcEnabled'] != showing.cc_enabled) or
                                    (showing_types['isDsEnabled'] and showing_types[
                                        'isDsEnabled'] != showing.ds_enabled)
                                ):
                                    new_shows_with_cc.append(f"{showing}")
                                showing.save()
    for existing_show in existing_shows.values():
        existing_show._visible = False
        existing_show.save()
    if len(new_shows_with_cc) > 0:
        new_shows_with_cc = "<br>\n".join(new_shows_with_cc)
        send_alerts(new_shows_with_cc)
    print(f"{date}-polling done")


def send_alerts(showings: str):
    send_email(showings)
    send_sms()
    print(f"all enabled alerts sent to me")


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


def send_sms():
    # https://www.fullstackpython.com/blog/send-sms-text-messages-python.html
    body = f"More tickets available in CC for movies"
    # the following line needs your Twilio Account SID and Auth Token
    client = Client(f"{os.environ['TWILIO_ACCOUNT_SID']}", f"{os.environ['TWILIO_AUTH_TOKEN']}")

    # change the "from_" number to your Twilio number and the "to" number
    # to the phone number you signed up for Twilio with, or upgrade your
    # account to send SMS to any phone number
    client.messages.create(to=f"{os.environ['TO_NUMBER']}",
                           from_=f"{os.environ['TWILIO_VIRTUAL_NUMBER']}",
                           body=body)
    print(f"text sent to {os.environ['TO_NUMBER']} for new CC movies")


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(func=poll_which_cineplex_movies_are_available, hour=17, trigger='cron')
    scheduler.add_job(func=poll_cineplex_showings, hours=1, trigger='interval')
    scheduler.start()
