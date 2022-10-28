from django.urls import path

from cineplex_website.views import Index

urlpatterns = [
    path('', Index.as_view(), name="index"),
]