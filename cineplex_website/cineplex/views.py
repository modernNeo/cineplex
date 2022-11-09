import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View

from cineplex.models import DateToQuery, Showing

# Create your views here.
from poll_cineplex.poll_cineplex import poll_cineplex


class Index(View):

    def get(self, request):
        if request.GET.get('poll_site', None) is not None and request.GET['poll_site']:
            poll_cineplex()
            return HttpResponseRedirect("/?message=polling%20done")
        return render(
            request, 'index.html',
            context={
                "message": request.GET.get("message", None),
                'current_date': datetime.datetime.now().strftime("%Y/%m/%d"),
                'dates': DateToQuery.objects.all()
            }
        )


class AuditLogs(View):

    def get(self, request):
        if request.GET.get('poll_site', None) is not None and request.GET['poll_site']:
            poll_cineplex()
            return HttpResponseRedirect("/audit_logs?message=polling%20done")
        return render(
            request,
            'audit_logs.html',
            context={
                "showings": reversed(sorted(Showing.objects.all(), key=lambda x: x.get_latest_update_date))
            }
        )
