
import requests
from django.conf import settings


def _call_api(params):
    resp = requests.get(
        settings.OMDB_API_URL, params={"apikey": settings.OMDB_API_KEY, 'type': 'movie', **params}
    )
    resp.raise_for_status()
    data = resp.json()

    if data["Response"] != "True":
        raise Exception(data["Error"])

    if data["Type"] != "movie":
        raise Exception(f'{data["Title"]} is not a movie.')

    return data


def fetch_movie_by_id(id):
    params = {'i': id}
    return _call_api(params)


def fetch_movie_by_title(title):
    params = {'t': title}
    return _call_api(params)
