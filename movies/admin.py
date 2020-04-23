from django.contrib import admin
from django.utils.safestring import mark_safe

from mymdb.admin import Admin

from .models import Genre, Movie


@admin.register(Movie)
class MovieAdmin(Admin):
    readonly_fields = ("id", "image", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    readonly_fields,
                    "imdb_id",
                    "title",
                    "year",
                    "runtime",
                    "language",
                    "awards",
                    "poster",
                    "imdb_rating",
                    "metascore",
                    "on_watchlist",
                    "in_store",
                    "genres",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "imdb_id",
                    "title",
                    "year",
                    "runtime",
                    "language",
                    "awards",
                    "poster",
                    "imdb_rating",
                    "metascore",
                    "on_watchlist",
                    "in_store",
                    "genres",
                ),
            },
        ),
    )

    list_display = (
        "title",
        "thumb",
        "year",
        "runtime",
        "get_genres",
        "imdb_rating",
        "metascore",
        "on_watchlist",
        "in_store",
    )
    list_filter = ("on_watchlist", "in_store", "genres")
    ordering = ("-imdb_rating", "-metascore")
    search_fields = ("title",)

    def get_genres(self, obj):
        return ", ".join([m.title for m in obj.genres.all()])

    def image(self, obj):
        return mark_safe(
            f'<a href="https://www.imdb.com/title/{obj.imdb_id}"><img src="{obj.poster}"/></a>'
        )

    def thumb(self, obj):
        return mark_safe(
            f'<a href="https://www.imdb.com/title/{obj.imdb_id}"><img src="{obj.poster}" width="60"/></a>'
        )


@admin.register(Genre)
class GenreAdmin(Admin):
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = ((None, {"fields": (readonly_fields, "title",)},),)
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("title",)},),)

    list_display = ("title",)
    ordering = ("title",)
    search_fields = ("title",)
