import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LinkKind(Enum):  # urls that is possible to see in iranintl
    UNKNOWN = -1
    MAIN_PAGE = 0
    LIVE_BLOG = 1
    ARTICLE = 2
    VIDEO = 3


class Link:
    def __init__(self, url: str, title: str):
        self.title = title
        self.url = url
        self.kind: LinkKind = Link.decide_link_kind(url)

    @staticmethod
    def __is_article_url(url: str):  # https://www.iranintl.com/202506267498
        splits = url.split("/")
        return len(splits) == 4 and splits[-1].isdigit()

    @staticmethod
    def decide_link_kind(url: str):
        if not url.startswith("https://www.iranintl.com"):
            logging.debug(f"unknown url: {url}")
            return LinkKind.UNKNOWN
        if url == "https://www.iranintl.com" or url == "https://www.iranintl.com/":
            return LinkKind.MAIN_PAGE
        if (
            "liveblog" in url
        ):  # https://www.iranintl.com/fa/liveblog/live-update-jun26-2025#202506278977
            return LinkKind.LIVE_BLOG
        if (
            "video" in url
        ):  # https://www.iranintl.com/fa/video/ott_56b60da21444407c870c612451cbf9c3
            return LinkKind.VIDEO
        if Link.__is_article_url(url):
            return LinkKind.ARTICLE

        logging.debug(f"unknown url: {url}")
        return LinkKind.UNKNOWN

    def to_dict(self):
        return {"title": self.title, "url": self.url, "kind": self.kind}


class Article:# https://www.iranintl.com/202506282966
    def __init__(
        self,
        header: str,
        publish_datetime: datetime,
        update_datetime: datetime,
        paragraphs: list[str],
        urls: list[Link],
    ):
        self.header = header
        self.publish_datetime = publish_datetime
        self.update_datetime = update_datetime
        self.paragraphs = paragraphs
        self.urls = urls


class LiveBlog:
    def __init__(self, header: str, articles: list[Article]): # Article here has small(2 or 3) amount of paragraphs
        self.header = header
        self.articles = articles


class Video: # https://www.iranintl.com/fa/video/ott_e2c875cdb6694e9188f96f809b45dd72
    def __init__(
        self,
        header: str,
        video_desc: str,
        publish_datetime: datetime,
        video_caption: str,
    ):
        self.header = header
        self.video_desc = video_desc
        self.publish_datetime = publish_datetime
        self.video_caption = video_caption
