import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View

from cineplex.models import DateToQuery, Showing, Movie

# Create your views here.
from cineplex_poller_app.cineplex_poller import poll_cineplex_showings


class Index(View):

    def get(self, request):
        if request.GET.get('poll_site', None) is not None and request.GET['poll_site']:
            poll_cineplex_showings()
            return HttpResponseRedirect("/?message=polling%20done")
        return render(
            request, 'index.html',
            context={
                "message": request.GET.get("message", None),
                'current_date': datetime.datetime.now().strftime("%Y/%m/%d"),
                "movies": Movie.get_all_showings(),
                'dates': DateToQuery.objects.all()
            }
        )


class AuditLogs(View):

    def get(self, request):
        if request.GET.get('poll_site', None) is not None and request.GET['poll_site']:
            poll_cineplex_showings()
            return HttpResponseRedirect("/audit_logs?message=polling%20done")
        return render(
            request,
            'audit_logs.html',
            context={
                "showings": reversed(sorted(Showing.objects.all(), key=lambda x: x.get_latest_update_date))
            }
        )
