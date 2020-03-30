import os

from django.core.management.base import BaseCommand, CommandError

from movies.models import Genre, Movie


class Command(BaseCommand):
    help = "Update the movie database from a directory of movies"

    def add_arguments(self, parser):
        parser.add_argument("PATH", type=str, help="The path to look for movies")

    def handle(self, *args, **options):
        items = os.listdir(options["PATH"])
        for i, item in enumerate(items):
            print(f'[{i+1}/{len(items)}] "{item}"...', end=" ", flush=True)
            # TODO: search IMDB
            print("Done")
