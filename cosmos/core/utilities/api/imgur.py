import aiohttp


class ImgurHTTPException(Exception):

    ...


class ImgurImage(object):

    def __init__(self, *, title, animated, link, **_kwargs):
        self.title = title
        self.animated = animated
        self.url = link


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


class ImgurClient(object):

    def __init__(self, client_id):
        self.id = client_id
        self.http = ImgurHTTPClient(self)

    async def upload(self, image, video=None, title=str()):
        data = await self.http.upload(title=title, image=image, video=video)
        return ImgurImage(**data)
