from django.contrib import admin

from mymdb.admin import Admin

from .models import Genre, Movie


@admin.register(Movie)
class MovieAdmin(Admin):
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    readonly_fields,
                    "imdb_id",
                    "title",
                    "year",
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
        "imdb_rating",
        "metascore",
        "on_watchlist",
        "in_store",
    )
    ordering = ("imdb_rating",)
    search_fields = ("title",)


@admin.register(Genre)
class GenreAdmin(Admin):
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = ((None, {"fields": (readonly_fields, "title",)},),)
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("title",)},),)

    list_display = ("title",)
    ordering = ("title",)
    search_fields = ("title",)
