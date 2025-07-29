from typing import Annotated, Optional

from aiohttp import ClientSession, ClientTimeout
from pydantic import Field, validate_call

from .creator import Creator
from .parser import Parser
from .post import Post, filter_posts_from_start_id, filter_posts_with_media


class AsyncCreator(Creator):
    def __init__(
        self,
        name: Optional[str] = None,
        data: Optional[dict] = None,
        parser: Optional[Parser] = None,
    ):
        super().__init__(name, data, parser)

    @validate_call
    async def get_posts(
        self,
        start_id: int = -1,
        offset_limit: int = 2**64 - 1,
        q: Optional[Annotated[str, Field(min_length=3)]] = None,
    ):
        offset = 0
        step = 50
        url = self.parser.fmt_get_posts_url.format(self=self)
        params = {"q": q} if q else {}

        while offset < offset_limit:  # Проверяем, что offset не превышает лимит
            params["o"] = offset

            async with ClientSession(
                timeout=ClientTimeout(total=self.parser.timeout)
            ) as session:
                async with session.get(url, params=params) as r:
                    if r.status != 200:
                        break
                    posts = await r.json()

                    if not posts:  # Если данные закончились, выходим из цикла
                        break

            posts = [Post(data=post, parser=self.parser) for post in posts]

            if self.parser.skip_posts_without_media:
                posts = filter_posts_with_media(posts)
            if start_id != -1:
                posts = filter_posts_from_start_id(posts, start_id)
            for post in posts:
                yield post

            offset += step
