import datetime

from django.db import models


# Create your models here.

class DateToQuery(models.Model):
    date = models.DateField()

    @property
    def get_date(self):
        return self.date.strftime('%Y/%m/%d')

    def __str__(self):
        return f"{self.get_date}"


class Movie(models.Model):
    name = models.TextField()
    filmId = models.IntegerField()

    def __str__(self):
        return f"{self.name}"


class MovieAndDateIntersection(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    date = models.ForeignKey(DateToQuery, on_delete=models.CASCADE)


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
    audit_log = models.TextField()
    visible = models.BooleanField(default=True)
    last_row = models.TextField()
    payment_url = models.TextField()

    @property
    def get_date(self):
        return self.date.strftime("%Y/%m/%d")

    def save(self, *args, **kwargs):
        date = datetime.datetime.now().strftime("%Y/%m/%d - %-H:%M:%S")
        if self.id is None:
            print("new showing being saved")
            self.audit_log = f"{date}-showing added\n"
        if getattr(self, "_seatsRemaining", None) is not None and self._seatsRemaining != self.seatsRemaining:
            self.audit_log += (
                f"{date}-changing seats remaining from {self.seatsRemaining} to {self._seatsRemaining}\n"
            )
            self.seatsRemaining = self._seatsRemaining
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_cc_enabled", None) is not None and self._cc_enabled != self.cc_enabled:
            self.audit_log += (
                f"{date}-changing seats remaining from {self.cc_enabled} to {self._cc_enabled}\n"
            )
            self.cc_enabled = self._cc_enabled
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_ds_enabled", None) is not None and self._ds_enabled != self.ds_enabled:
            self.audit_log += (
                f"{date}-changing seats remaining from {self.ds_enabled} to {self._ds_enabled}\n"
            )
            self.ds_enabled = self._ds_enabled
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_visible", None) is not None and self._visible != self.visible:
            self.audit_log += (
                f"{date}-changing seats remaining from {self.visible} to {self._visible}\n"
            )
            self.visible = self._visible
            print(f"{self.id}-existing showing being updated")
        super(Showing, self).save(*args, **kwargs)

    def __str__(self):
        return f"Movie: {self.movie} - Time: {self.date} {self.time.strftime('%I:%M %p')} - CC: {self.cc_enabled} - Showing Type:  {self.showing_type} | {self.auditorium} | Last Row: {self.last_row}"
