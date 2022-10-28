from django.contrib import admin

# Register your models here.
from cineplex.models import DateToQuery, Movie, MovieAndDateIntersection, Showing


class DateToQueryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
    )


admin.site.register(DateToQuery, DateToQueryAdmin)


class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'filmId'
    )


admin.site.register(Movie, MovieAdmin)


class MovieAndDateIntersectionAdmin(admin.ModelAdmin):
    list_display = (
        'movie', 'date'
    )


admin.site.register(MovieAndDateIntersection, MovieAndDateIntersectionAdmin)


class ShowingAdmin(admin.ModelAdmin):
    list_display = (
        'movie', 'date', 'time', 'showing_type', 'auditorium', 'cc_enabled', 'last_row'
    )


admin.site.register(Showing, ShowingAdmin)
