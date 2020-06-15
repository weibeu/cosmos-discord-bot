import datetime as dt
import aiohttp


class ImgurHTTPException(Exception):

    ...


class ImgurImage(object):

    def __init__(self, *, title, animated, link, datetime=None, **kwargs):
        self.title = title
        self.animated = animated
        self.url = link
        self.__set_meta(kwargs)
        self.datetime = datetime

    @property
    def timestamp(self):
        try:
            return dt.datetime.fromtimestamp(self.datetime)
        except TypeError:
            pass

    def __set_meta(self, data):
        for name, value in data.items():
            self.__setattr__(name, value)


class ImgurHTTPClient(object):

    API_BASE_URL = "https://api.imgur.com/3"

    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()

    def __get_headers(self):
        return {
            "Authorization": f"Client-ID {self.client.id}",
        }

    @staticmethod
    def __fix_body(body):
        return {key: value for key, value in body.items() if value}

    async def request(self, route, method="POST", data=None, **kwargs):
        url = f"{self.API_BASE_URL}{route}"
        data = self.__fix_body(data or dict())
        async with self.session.request(
                method, url, data=data, headers=self.__get_headers(), **kwargs) as response:
            if response.status != 200:
                raise ImgurHTTPException
            return await response.json()

    async def upload(self, title=None, image=None, video=None):
        body = dict(title=title, image=image, video=video)
        json = await self.request('/upload/', data=body)
        return json["data"]

    async def fetch_meta(self, hash_):
        json = await self.request(f'/image/{hash_}', method="GET")
        return json["data"]


class ImgurClient(object):

    def __init__(self, client_id):
        self.id = client_id
        self.http = ImgurHTTPClient(self)

    @staticmethod
    def get_image_hash(image):
        url = image.url if isinstance(image, ImgurImage) else image
        if "imgur.com" in url:
            try:
                return url.split("/")[-1].split(".")[0]
            except IndexError:
                pass
        return image

    async def fetch_meta(self, hash_):
        hash_ = self.get_image_hash(hash_)
        data = await self.http.fetch_meta(hash_)
        return ImgurImage(**data)

    async def upload(self, image=None, video=None, title=str()):
        data = await self.http.upload(title=title, image=image, video=video)
        return ImgurImage(**data)
