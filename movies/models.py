from django.db import models
from django.utils.translation import gettext_lazy as _

from mymdb.models import Model


class Genre(Model):
    title = models.CharField(_("title"), max_length=150, unique=True)

    def __str__(self):
        return self.title


class Movie(Model):
    imdb_id = models.CharField(_("IMDB ID"), max_length=150, unique=True)
    title = models.CharField(_("Title"), max_length=150)
    year = models.IntegerField(_("Year"))
    language = models.CharField(_("Title"), max_length=150)
    awards = models.TextField(_("Awards"))
    poster = models.URLField(_("Poster"))
    imdb_rating = models.FloatField(_("IMDB Rating"), null=True)
    metascore = models.FloatField(_("Metascore"), null=True)
    on_watchlist = models.BooleanField(_("On Watchlist"))
    in_store = models.BooleanField(_("In Store"))

    genres = models.ManyToManyField(Genre, related_name="movies")

    def __str__(self):
        return self.title
