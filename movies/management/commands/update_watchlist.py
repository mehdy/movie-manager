import os

from django.core.management.base import BaseCommand, CommandError

from movies.models import Genre, Movie


class Command(BaseCommand):
    help = "Update the movie database from an IMDB watchlist URL"

    def add_arguments(self, parser):
        parser.add_argument("URL", type=str, help="The URL to look for movies")

    def handle(self, *args, **options):
        # TODO: Extract the list of movies
        items = []
        for i, item in enumerate(items):
            print(f'[{i+1}/{len(items)}] "{item}"...', end=" ", flush=True)
            # TODO: Get movie detail
            print("Done")
