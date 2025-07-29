from typing import Annotated, Optional

from pydantic import Field, validate_call
from requests import get

from .parser import Parser
from .post import Post, filter_posts_from_start_id, filter_posts_with_media


class Creator:
    def __init__(
        self,
        name: Optional[str] = None,
        data: Optional[dict] = None,
        parser: Optional[Parser] = None,
    ):
        self.parser = parser if parser else Parser()

        if name:
            data = self.parser.get_creator(value=name, search_by="name")
        if data:
            self.parse(data)
        else:
            raise ValueError(
                f"{name=} not found in 'creators, or {data=} cant be None '"
            )
        self.icons_url = self.parser.fmt_icons_url.format(self=self)
        self.banners_url = self.parser.fmt_banners_url.format(self=self)

    def __str__(self) -> str:
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"Creator({attributes})"

    def parse(self, data):
        self.name = data.get("name")
        self.id = data.get("id")
        self.service = data.get("service")
        self.indexed = data.get("indexed")
        self.updated = data.get("updated")
        self.favorited = data.get("favorited")

    @validate_call
    def get_posts(
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
            r = get(url, timeout=self.parser.timeout, params=params)
            if r.status_code != 200:
                break
            posts = r.json()

            if not posts:  # Если данные закончились, выходим из цикла
                break

            posts = [Post(data=post, parser=self.parser) for post in posts]

            if self.parser.skip_posts_without_media:
                posts = filter_posts_with_media(posts)
            if start_id != -1:
                posts = filter_posts_from_start_id(posts, start_id)
            for post in posts:
                yield post

            offset += step  # Увеличиваем offset на шаг 50
