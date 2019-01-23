import aiohttp


class HasteBinURL(object):

    BASE = "https://hastebin.com/"

    def __init__(self, response_key):
        self._response_key = response_key

    @property
    def url(self):
        return self.BASE + self._response_key

    @property
    def py(self):
        return self.url + ".py"

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url


class HasteBin(object):

    BASE_URL = "https://hastebin.com/documents"
    ENCODING = "utf-8"

    async def haste(self, content: str) -> HasteBinURL:
        content = str(content)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL, data=content.encode(self.ENCODING)) as post:
                response = await post.json()
                return HasteBinURL(response["key"])
