import datetime

from django.db import models


# Create your models here.

class DateToQuery(models.Model):
    date = models.DateField()

    @property
    def get_front_end_date(self):
        return self.date.strftime('%Y/%m/%d')

    def __str__(self):
        return f"{self.get_front_end_date}"


class Movie(models.Model):
    name = models.TextField()
    filmId = models.IntegerField()

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_all_showings(cls):
        showings = {}
        dates_to_query = DateToQuery.objects.all()
        for date_to_query in dates_to_query:
            movies_and_dates = date_to_query.movieanddateintersection_set.all()
            for movies_and_date in movies_and_dates:
                front_end_date = movies_and_date.date.get_front_end_date
                date_obj = movies_and_date.date.date
                movie = movies_and_date.movie
                showings[front_end_date] = {
                    movie.name: {
                        'UltraAVX 3D D-BOX': movie.showing_set.all()
                        .filter(
                            date=date_obj, showing_type='UltraAVX 3D D-BOX'
                        ).order_by('time'),
                        'UltraAVX 3D': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='UltraAVX 3D').order_by('time'),
                        'UltraAVX D-BOX': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='UltraAVX D-BOX').order_by('time'),
                        'UltraAVX': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='UltraAVX').order_by('time'),
                        'VIP 19+ 3D CC': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='VIP 19+ 3D',cc_enabled=True).order_by('time'),
                        'VIP 19+ 3D': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='VIP 19+ 3D',cc_enabled=False).order_by('time'),
                        'VIP 19+ CC': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='VIP 19+',cc_enabled=True).order_by('time'),
                        'VIP 19+': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='VIP 19+',cc_enabled=False).order_by('time'),
                        '3D CC': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='3D',cc_enabled=True).order_by('time'),
                        '3D': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='3D', cc_enabled=False).order_by('time'),
                        'Regular': movie.showing_set.all()
                        .filter(date=date_obj, showing_type='Regular').order_by('time')
                    }
                }
                total_showings_on_date = movie.showing_set.all().filter(date=date_obj) \
                    .exclude(showing_type='UltraAVX 3D D-BOX') \
                    .exclude(showing_type='UltraAVX 3D') \
                    .exclude(showing_type='UltraAVX D-BOX') \
                    .exclude(showing_type='UltraAVX') \
                    .exclude(showing_type='VIP 19+ 3D') \
                    .exclude(showing_type='VIP 19+') \
                    .exclude(showing_type='3D') \
                    .exclude(showing_type='Regular')
                if len(total_showings_on_date) > 0:
                    raise Exception("more than 0 unaccounted for showings")
        return showings


class MovieAndDateIntersection(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date = models.ForeignKey(DateToQuery, on_delete=models.CASCADE)


date_format = "%Y/%m/%d"
date_str_strftime_format = f"{date_format} - %-H:%M:%S"
date_str_strptime_format = f"{date_format} - %H:%M:%S"


class Showing(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    cc_enabled = models.BooleanField(default=False)
    ds_enabled = models.BooleanField(default=False)
    showing_type = models.TextField()
    auditorium = models.TextField()
    seatsRemaining = models.IntegerField(default=0)
    seatMapUrl = models.TextField()
    visible = models.BooleanField(default=True)
    last_row = models.TextField(null=True)
    payment_url = models.TextField()

    @property
    def get_date(self):
        return self.date.strftime(date_format)

    def save(self, *args, **kwargs):
        current_date = datetime.datetime.now()
        date = current_date.strftime(date_str_strftime_format)
        audit_log = None
        if self.id is None:
            print(f"new showing being saved")
            audit_log = f"showing added\n"
        if getattr(self, "_seatsRemaining", self.seatsRemaining) != self.seatsRemaining:
            audit_log = f"changing seats remaining from {self.seatsRemaining} to {self._seatsRemaining}\n"
            self.seatsRemaining = self._seatsRemaining
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_cc_enabled", self.cc_enabled) != self.cc_enabled:
            audit_log = f"changing seats remaining from {self.cc_enabled} to {self._cc_enabled}\n"
            self.cc_enabled = self._cc_enabled
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_ds_enabled", self.ds_enabled) != self.ds_enabled:
            audit_log = f"changing seats remaining from {self.ds_enabled} to {self._ds_enabled}\n"
            self.ds_enabled = self._ds_enabled
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_visible", self.visible) != self.visible:
            audit_log = f"changing visibility from {self.visible} to {self._visible}\n"
            self.visible = self._visible
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_last_row", self.last_row) != self.last_row:
            audit_log = f"changing last row from {self.last_row} to {self._last_row}\n"
            self.last_row = self._last_row
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_time", self.time) != self.time:
            audit_log = f"changing time from {self.time} to {self._time}\n"
            self.time = self._time
            print(f"{self.id}-existing showing being updated")
        super(Showing, self).save(*args, **kwargs)
        if audit_log is not None:
            AuditLog(time_audited=current_date, audit_log=audit_log, showing=self).save()

    @property
    def get_latest_update_date(self):
        return self.auditlog_set.all().order_by('-time_audited')[0].time_audited

    @property
    def get_latest_updates(self):
        return self.auditlog_set.all().order_by('-time_audited')

    @property
    def get_front_end_string(self):
        return f"Time: {self.date} {self.time.strftime('%I:%M %p')} {self.auditorium} | Last Row: {self.last_row}"

    def __str__(self):
        return f"Movie: {self.movie} - Time: {self.date} {self.time.strftime('%I:%M %p')} - CC: {self.cc_enabled} - Showing Type:  {self.showing_type} | {self.auditorium} | Last Row: {self.last_row}"


class AuditLog(models.Model):
    time_audited = models.DateTimeField()
    audit_log = models.TextField()
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.time_audited} {self.audit_log}"
