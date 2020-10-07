"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from . import BaseAPIHTTPClient

import datetime


class TMDBAPIException(Exception):

    pass


class Cast(object):

    def __init__(self, *, character, name, order, **_kwargs):
        self.name = name
        self.order = order
        self.character = character


class Crew(object):

    def __init__(self, *, department, job, name, **_kwargs):
        self.name = name
        self.job = job
        self.department = department


class Credits(object):

    def __init__(self, *, cast, crew, **_kwargs):
        self.cast = sorted([Cast(**_) for _ in cast], key=lambda c: c.order)
        self.crew = [Crew(**_) for _ in crew]
        self.director = self.__get_crew_with_job("DIRECTOR")
        self.writer = self.__get_crew_with_job("WRITER")
        self.screenplay = self.__get_crew_with_job("SCREENPLAY")

    def __get_crew_with_job(self, job):
        try:
            return [crew for crew in self.crew if crew.job.upper() == job.upper()][0]
        except IndexError:
            return


class PartialMovie(object):

    DEFAULT_SIZE = "original"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/{size}{file_path}"

    def _get_image_url(self, path, size=DEFAULT_SIZE):
        return self.IMAGE_BASE_URL.format(size=size, file_path=path)

    @staticmethod
    def _get_datetime(string):
        try:
            return datetime.datetime.strptime(string, "%Y-%m-%d")
        except (ValueError, TypeError):
            return

    def __init__(self, *, poster_path, adult, overview, original_title, **kwargs):
        self.id = kwargs["id"]
        self.title = original_title
        self.nsfw = adult
        self.overview = overview
        self.poster = self._get_image_url(poster_path)
        self.credits = kwargs.get("credits")


class Movie(PartialMovie):

    def __init__(
            self, *, genres, homepage, budget, imdb_id, release_date,
            revenue, vote_count, production_companies, status,
            spoken_languages, production_countries, **kwargs
    ):
        super().__init__(**kwargs)
        self.homepage = homepage
        self.genres = [g["name"] for g in genres]
        self.budget = budget
        self.imdb_id = imdb_id
        self.revenue = revenue
        self.votes = vote_count
        self.status = status
        self.release_date = self._get_datetime(release_date)
        self.productions = [p["name"] for p in production_companies]
        self.languages = [l["name"] for l in spoken_languages]
        self.countries = [c["name"] for c in production_countries]


class TMDBHTTPClient(BaseAPIHTTPClient):

    API_BASE_URL = "https://api.themoviedb.org/3"
    BASE_EXCEPTION = TMDBAPIException

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.client.access_token}"
        }

    async def fetch_movie_data(self, id_):
        return await self.request(f"/movie/{id_}", method="GET")

    async def search_movie(self, query):
        params = dict(query=query, include_adult="true")
        data = await self.request("/search/movie", method="GET", params=params)
        return data.get("results") or []

    async def fetch_movie_credits(self, movie_id):
        return await self.request(f"/movie/{movie_id}/credits", method="GET")


class TMDBClient(object):

    def __init__(self, access_token):
        self.access_token = access_token
        self.http = TMDBHTTPClient(self)

    async def fetch_movie(self, movie_id, fetch_credits=False) -> Movie:
        data = await self.http.fetch_movie_data(movie_id)
        credits_ = await self.http.fetch_movie_credits(movie_id) if fetch_credits else None
        return Movie(**data, credits=Credits(**credits_))

    async def search_movie(self, query) -> list:
        results = await self.http.search_movie(query)
        return [PartialMovie(**_) for _ in results]

    async def fetch_movie_from_search(self, query, fetch_credits=True) -> Movie:
        results = await self.search_movie(query)
        try:
            return await self.fetch_movie(results[0].id, fetch_credits)
        except IndexError:
            pass
