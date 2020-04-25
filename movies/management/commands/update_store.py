import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

from django.core.management.base import BaseCommand

from movies.models import Genre, Movie
from movies.omdb import fetch_movie_by_title


class Command(BaseCommand):
    help = "Update the movie database from a directory of movies"

    def add_arguments(self, parser):
        parser.add_argument("PATH", type=str, help="The path to look for movies")

    def handle_verbosity(self, v):
        self.logger = logging.getLogger(__name__)
        level = [logging.FATAL, logging.ERROR, logging.INFO, logging.DEBUG][v]
        logging.basicConfig(level=level)
        self.logger.setLevel(level)

    def searchable_name(self, name):
        return name.replace(".", " ").lower()

    def update_movie(self, data):
        try:
            movie = Movie.objects.get(imdb_id=data["imdbID"])
            movie.in_store = True
            movie.save()
            self.logger.info(f'Marked "{movie.title}" exist in store.')
            return
        except Movie.DoesNotExist:
            pass

        runtime = -1
        try:
            runtime = int(data["Runtime"].split()[0])
        except Exception:
            pass

        try:
            movie = Movie.objects.create(
                imdb_id=data["imdbID"],
                title=data["Title"],
                year=int(data["Year"]),
                runtime=runtime,
                language=data["Language"],
                awards=data["Awards"],
                poster=data["Poster"],
                imdb_rating=float(data["imdbRating"])
                if data["imdbRating"] != "N/A"
                else None,
                metascore=float(data["Metascore"])
                if data["Metascore"] != "N/A"
                else None,
                on_watchlist=False,
                in_store=True,
            )
            movie.genres.add(
                *[
                    Genre.objects.get_or_create(title=title.strip())[0].pk
                    for title in data["Genre"].split(",")
                ]
            )
        except Exception as e:
            self.logger.error(f'Failed to create movie "{id}": {e}')
            raise e

        self.logger.info(f'Added "{movie.title}" successfully')

    def fetch_movie(self, name):
        sname = self.searchable_name(name)
        self.logger.debug(f'Fetching "{sname}"...')
        try:
            data = fetch_movie_by_title(sname)
        except Exception as e:
            self.logger.error(f'Failed to fetch "{sname}": {e}')
            return
        self.update_movie(data)

    def fetch_movies(self, names):
        with ThreadPoolExecutor(max_workers=32) as pool:
            futures = [pool.submit(partial(self.fetch_movie, name)) for name in names]

        oks, errors = 0, 0
        for future in as_completed(futures):
            if future.exception():
                errors += 1
            else:
                oks += 1

        self.logger.info(f"{oks} tasks completed successfully out of {len(futures)}")
        if errors > 0:
            self.logger.error(f"{errors} tasks failed to complete successfully")

    def handle(self, *args, **options):
        self.handle_verbosity(options["verbosity"])
        self.fetch_movies(os.listdir(options["PATH"]))
