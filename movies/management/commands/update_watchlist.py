import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

import requests
from django.core.management.base import BaseCommand
from imdb import IMDb

from movies.models import Genre, Movie


class Command(BaseCommand):
    help = "Update the movie database from an IMDB watchlist URL"

    def add_arguments(self, parser):
        parser.add_argument("URL", type=str, help="The URL to look for movies")

    def handle_verbosity(self, v):
        self.logger = logging.getLogger(__name__)
        level = [logging.FATAL, logging.ERROR, logging.INFO, logging.DEBUG][v]
        self.logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter())
        self.logger.addHandler(handler)
        self.logger.info("Starting...")

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
            data = self.imdb.get_movie(id[2:], info=["main", "critic_reviews"])
            if data["kind"] != "movie":
                raise Exception(f'{data["title"]} is not a movie.')
        except Exception as e:
            self.logger.error(f'Failed to fetch "{id}": {e}')
            return

        runtime = -1
        try:
            runtime = int(data["runtimes"][0])
        except Exception:
            pass

        try:
            movie = Movie.objects.create(
                imdb_id=id,
                title=data["title"],
                year=data["year"],
                runtime=runtime,
                language=", ".join(data.get("languages", [])),
                poster=data["cover url"],
                imdb_rating=data.get("rating", -1),
                metascore=float(data.get("metascore", -1)),
                on_watchlist=True,
                in_store=False,
            )
            movie.genres.add(
                *[
                    Genre.objects.get_or_create(title=title.strip())[0].pk
                    for title in data["genres"]
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

        with ThreadPoolExecutor(max_workers=32) as pool:
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

        self.imdb = IMDb()

        result = self.fetch_url(options["URL"])
        ids = self.extract_movies_id(result)
        self.fetch_movies(ids)
        self.logger.info("Updated watchlist sucessfully")
