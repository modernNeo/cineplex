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
        date = datetime.datetime.now().strftime(date_str_strftime_format)
        audit_log = None
        if self.id is None:
            print(f"{date}-new showing being saved")
            audit_log = f"{date}-showing added\n"
        if getattr(self, "_seatsRemaining", self.seatsRemaining) != self.seatsRemaining:
            audit_log = (
                f"{date}-changing seats remaining from {self.seatsRemaining} to {self._seatsRemaining}\n"
            )
            self.seatsRemaining = self._seatsRemaining
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_cc_enabled", self.cc_enabled) != self.cc_enabled:
            audit_log = (
                f"{date}-changing seats remaining from {self.cc_enabled} to {self._cc_enabled}\n"
            )
            self.cc_enabled = self._cc_enabled
            print(f"{self.id}-existing showing being updated")

        if getattr(self, "_ds_enabled", self.ds_enabled) != self.ds_enabled:
            audit_log = (
                f"{date}-changing seats remaining from {self.ds_enabled} to {self._ds_enabled}\n"
            )
            self.ds_enabled = self._ds_enabled
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_visible", self.visible) != self.visible:
            audit_log = (
                f"{date}-changing seats remaining from {self.visible} to {self._visible}\n"
            )
            self.visible = self._visible
            print(f"{self.id}-existing showing being updated")
        if getattr(self, "_last_row", self.last_row) != self.last_row:
            audit_log = (
                f"{date}-changing last row from {self.last_row} to {self._last_row}\n"
            )
            
            self.last_row = self._last_row
            print(f"{self.id}-existing showing being updated")
        super(Showing, self).save(*args, **kwargs)
        if audit_log is not None:
            AuditLog(time_audited=date, audit_log=audit_log, showing=self).save()

    @property
    def get_latest_update_date(self):
        return self.auditlog_set.all().order_by('-time_audited')[0].time_audited

    @property
    def get_latest_update(self):
        return self.auditlog_set.all().order_by('-time_audited')

    def __str__(self):
        return f"Movie: {self.movie} - Time: {self.date} {self.time.strftime('%I:%M %p')} - CC: {self.cc_enabled} - Showing Type:  {self.showing_type} | {self.auditorium} | Last Row: {self.last_row}"


class AuditLog(models.Model):
    time_audited = models.DateTimeField()
    audit_log = models.TextField()
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)
