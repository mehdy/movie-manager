import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

import requests
from django.core.management.base import BaseCommand

from movies.models import Genre, Movie
from movies.omdb import fetch_movie_by_id


class Command(BaseCommand):
    help = "Update the movie database from an IMDB watchlist URL"

    def add_arguments(self, parser):
        parser.add_argument("URL", type=str, help="The URL to look for movies")

    def handle_verbosity(self, v):
        self.logger = logging.getLogger(__name__)
        level = [logging.FATAL, logging.ERROR, logging.INFO, logging.DEBUG][v]
        logging.basicConfig(level=level)
        self.logger.setLevel(level)

    def fetch_url(self, url):
        self.logger.info(f'Fetching data from "{url}..."')
        resp = requests.get(url)
        self.logger.info(f'GET "{url}" status code: {resp.status_code}')
        self.logger.debug(f"response body: {resp.text}")
        if not resp.ok:
            self.logger.fatal(f'Failed to fetch data from "{url}": {resp.status_code}')
            return exit(1)
        return resp.text

    def extract_movies_id(self, data):
        self.logger.info(f"Extracting movies...")
        jdata = json.loads(re.search(r"\((?P<data>\{.*\})\)", data).groupdict()["data"])

        self.logger.info(f'Found {len(jdata["list"]["items"])} titles')
        return list(map(lambda movie: movie["const"], jdata["list"]["items"]))

    def fetch_movie(self, id):
        self.logger.info(f"Fetching movie {id}...")
        try:
            movie = Movie.objects.get(imdb_id=id)
            movie.on_watchlist = True
            movie.save()
            self.logger.info(f'Marked "{movie.title}" on watchlist')
            return
        except Movie.DoesNotExist:
            pass

        try:
            data = fetch_movie_by_id(id)
        except Exception as e:
            self.logger.error(f'Failed to fetch "{id}": {e}')
            return

        try:
            movie = Movie.objects.create(
                imdb_id=id,
                title=data["Title"],
                year=int(data["Year"]),
                language=data["Language"],
                awards=data["Awards"],
                poster=data["Poster"],
                imdb_rating=float(data["imdbRating"])
                if data["imdbRating"] != "N/A"
                else None,
                metascore=float(data["Metascore"])
                if data["Metascore"] != "N/A"
                else None,
                on_watchlist=True,
                in_store=False,
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

    def fetch_movies(self, ids):
        self.logger.info("Fetching data for each movie id")
        already_exists = Movie.objects.filter(imdb_id__in=ids, on_watchlist=True)
        self.logger.info(f"{already_exists.count()} already exists.")
        nonexistents = filter(
            lambda i: i not in already_exists.values_list("imdb_id", flat=True), ids
        )

        with ThreadPoolExecutor(max_workers=100) as pool:
            futures = [
                pool.submit(partial(self.fetch_movie, id)) for id in nonexistents
            ]

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

        result = self.fetch_url(options["URL"])
        ids = self.extract_movies_id(result)
        self.fetch_movies(ids)
        self.logger.info("Updated watchlist sucessfully")
