import aiohttp


class HasteBin(object):

    BASE = "https://hastebin.com/"
    BASE_URL = "https://hastebin.com/documents"
    ENCODING = "utf-8"

    async def haste(self, content: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL, data=content.encode(self.ENCODING)) as post:
                response = await post.json()
                return self.BASE + response["key"]
