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


def _get_datetime(string):
    try:
        return datetime.datetime.strptime(string, "%Y-%m-%d")
    except (ValueError, TypeError):
        return


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
        self.release_date = _get_datetime(release_date)
        self.productions = [p["name"] for p in production_companies]
        self.languages = [lang["name"] for lang in spoken_languages]
        self.countries = [c["name"] for c in production_countries]


class PartialTVShow(PartialMovie):

    def __init__(self, *, first_air_date, **kwargs):
        super().__init__(adult=None, original_title=kwargs["name"], **kwargs)
        self.first_air_date = _get_datetime(first_air_date)


class TVShowEpisode(object):

    def __init__(self, *, air_date, episode_number, name, overview, season_number, **_kwargs):
        self.air_date = _get_datetime(air_date)
        self.episode_number = episode_number
        self.name = name
        self.overview = overview
        self.season_number = season_number


class TVShowSeason(TVShowEpisode):

    def __init__(self, *, episode_count, **kwargs):
        super().__init__(**kwargs)
        self.episode_count = episode_count


class TVShow(Movie, PartialTVShow):

    def __init__(
            self, *, created_by, in_production, last_air_date, last_episode_to_air,
            next_episode_to_air, number_of_episodes, number_of_seasons, seasons, status, **kwargs
    ):
        Movie.__init__(
            self, budget=None, imdb_id=None, release_date=None,
            revenue=None, status=status, **kwargs
        )
        PartialTVShow.__init__(self, **kwargs)
        self.creators = [c["name"] for c in created_by]
        self.in_production = in_production
        self.last_air_date = _get_datetime(last_air_date)
        self.last_episode = TVShowEpisode(**last_episode_to_air)
        self.next_episode = TVShowEpisode(**next_episode_to_air) if next_episode_to_air else None
        self.episodes_count = number_of_episodes
        self.seasons_count = number_of_seasons
        self.seasons = seasons
        self.status = status
        self.type = kwargs.get("type")


class TMDBHTTPClient(BaseAPIHTTPClient):

    API_BASE_URL = "https://api.themoviedb.org/3"
    BASE_EXCEPTION = TMDBAPIException

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.client.access_token}"
        }

    async def fetch_movie_data(self, id_, extras=("credits", )):
        params = dict(append_to_response=",".join(extras))
        return await self.request(f"/movie/{id_}", method="GET", params=params)

    async def fetch_tvshow_data(self, id_, extras=("credits", )):
        params = dict(append_to_response=",".join(extras))
        return await self.request(f"/tv/{id_}", method="GET", params=params)

    async def search_movie(self, query):
        params = dict(query=query, include_adult="true")
        data = await self.request("/search/movie", method="GET", params=params)
        return data.get("results") or []

    async def search_tvshow(self, query):
        params = dict(query=query, include_adult="true")
        data = await self.request("/search/tv", method="GET", params=params)
        return data.get("results") or []

    async def search_any(self, query):
        params = dict(query=query, include_adult="true")
        data = await self.request("/search/multi", method="GET", params=params)
        return data.get("results") or []

    async def fetch_movie_credits(self, movie_id):
        return await self.request(f"/movie/{movie_id}/credits", method="GET")

    async def fetch_tvshow_credits(self, tvshow_id):
        return await self.request(f"/tv/{tvshow_id}/credits", method="GET")


class TMDBClient(object):

    def __init__(self, access_token):
        self.access_token = access_token
        self.http = TMDBHTTPClient(self)

    async def fetch_movie(self, movie_id) -> Movie:
        data = await self.http.fetch_movie_data(movie_id)
        return Movie(credits=Credits(**data.pop("credits")), **data)

    async def search_movie(self, query) -> list:
        results = await self.http.search_movie(query)
        return [PartialMovie(**_) for _ in results]

    async def fetch_movie_from_search(self, query) -> Movie:
        results = await self.search_movie(query)
        try:
            return await self.fetch_movie(results[0].id)
        except IndexError:
            pass

    async def fetch_tvshow(self, tvshow_id) -> TVShow:
        data = await self.http.fetch_tvshow_data(tvshow_id)
        return TVShow(credits=Credits(**data.pop("credits")), **data)

    async def search_tvshow(self, query) -> list:
        results = await self.http.search_tvshow(query)
        return [PartialTVShow(**_) for _ in results]

    async def fetch_tvshow_from_search(self, query) -> TVShow:
        results = await self.search_tvshow(query)
        try:
            return await self.fetch_tvshow(results[0].id)
        except IndexError:
            pass
