from .utils import download_creators, load_creators


class Parser:
    def __init__(
        self,
        domain: str = "coomer.su",
        skip_posts_without_media: bool = True,
        use_local_creators_file: bool = True,
        images_as_thumbnails: bool = True,  # replace domain to thumbmnail for images (works better)
        timeout: int = 7,
    ):
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.data_url = f"https://{domain}/data" # fixed 403 for media. added /data to url (data_url)
        self.api_url = f"https://{domain}/api/v1"
        self.thumbnail_url = f"https://img.{domain}/thumbnail/data"
        self.fmt_get_posts_url = "{self.parser.api_url}/{self.service}/user/{self.id}"
        self.fmt_icons_url = "https://img.{self.parser.domain}/icons/{self.service}/{self.id}"
        self.fmt_banners_url = "https://img.{self.parser.domain}/banners/{self.service}/{self.id}"
        self.fmt_file_url = self.data_url + "{path}"
        self.fmt_thumbnail_url = self.thumbnail_url + "{path}"
        self.skip_posts_without_media = skip_posts_without_media
        self.use_local_creators_file = use_local_creators_file
        self.images_as_thumbnails = images_as_thumbnails
        self.timeout = timeout
        if use_local_creators_file:
            self.creators = load_creators(domain)
        else:
            self.creators = download_creators(self.domain)

    def __str__(self) -> str:
        attributes = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"Parser({attributes})"

    def get_creator(self, value: str, search_by: str = "name"):
        return next(
            (item for item in self.creators if item.get(search_by) == value), None
        )
