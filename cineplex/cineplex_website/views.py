import datetime

from django.shortcuts import render
from django.views.generic.base import View

from cineplex_website.models import DateToQuery


# Create your views here.
class Index(View):

    def get(self, request):
        current_date = datetime.datetime.now().strftime("%Y/%m/%d")
        return render(request, 'index.html', context={'current_date': current_date, 'dates': DateToQuery.objects.all()})
