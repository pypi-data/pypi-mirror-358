from bs4 import BeautifulSoup
import requests
import random
import time
import logging
from ._utils import *
from .types import *

logger = logging.getLogger(__name__)


class IranIntl:

    def __init__(self, proxies=None, timeout=10):
        self.proxies = proxies
        self.timeout = timeout
        self.mainpage_url = "https://www.iranintl.com"

    def __fetch_html(self, url, headers={'User-Agent':'Mozilla'}):
        try:
            response = requests.get(
                url, headers=headers, proxies=self.proxies, timeout=self.timeout
            )
            response.raise_for_status()
            time.sleep(random.random())
            return response.content
        except requests.RequestException as e:
            logger.error(f"request failed for {url}: {str(e)}")
            raise

    def mainpage_links(
        self
    ) -> list[Link]:  # get all links in main page
        html = self.__fetch_html(self.mainpage_url)
        soup = BeautifulSoup(html, "html.parser")
        main_tag = soup.select_one("body > main > div")

        a_tags = main_tag.find_all("a")

        links = []
        for a_tag in a_tags:
            title = a_tag.get_text(strip=True)
            url = a_tag["href"]

            if title == "":  # look for image alt
                img = a_tag.find("img")
                title = img.get("alt", "")
            
            link = Link(url, title)
            links.append(link)

        return links

    def scrape_article(self, url: str):
        # h1
        # time
        # update_time
        # p
        # a (urls)
        html = self.__fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        article_tag = soup.find("article")
        header_tag = article_tag.find("header")
        main_tag = article_tag.find("main")

        header1_text = header_tag.find("h1").get_text(strip=True)

        time_tags = header_tag.find_all("time")
        publish_datetime = create_datetime(time_tags[0]["datetime"])
        update_datetime = create_datetime(time_tags[-1]["datetime"])

        p_tags = main_tag.find_all("p")
        paragraphs = [p.get_text("\n", strip=True) for p in p_tags]

        a_tags = article_tag.find_all("a")
        urls = [
            Link(title=a.get_text(strip=True), url=a["href"])
            for a in a_tags
            if a.get_text(strip=True) != ""
        ]

        return Article(
            header1_text, publish_datetime, update_datetime, paragraphs, urls
        )

    def scrape_liveblog(self, url: str) -> LiveBlog:
        html = self.__fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        parent_tag = soup.select_one("body > main > div > section")

        header1_tag = parent_tag.find("h1")
        header1_text = header1_tag.get_text(strip=True)

        article_tags = parent_tag.find_all("article")

        articles: list[Article] = []

        for article_tag in article_tags:
            time_tag = article_tag.find("time")
            dt = create_datetime(time_tag["datetime"])

            ps = [p.get_text(strip=True) for p in article_tag.find_all("p")]

            urls = [
                Link(title=u.get_text(strip=True), url=u["href"])
                for u in article_tag.find_all("a")
            ]

            header3_text = article_tag.find("h3").get_text(strip=True)

            article_obj = Article(header3_text, dt, dt, ps, urls)
            articles.append(article_obj)

        lb = LiveBlog(header1_text, articles)

        return lb

    def scrape_video(self, url: str) -> Video:
        html = self.__fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        main_tag = soup.select_one("body > main > div > section > main")

        # frame_class=main_tag.children[0]
        content_class = main_tag.find(
            "div", {"class": "video__content"}, recursive=False
        )

        header = content_class.find("h1").get_text(strip=True)
        desc = content_class.find("p").get_text(strip=True)
        date_dow = content_class.find("span", recursive=False).get_text(strip=True)

        datetime_date_dow = persian_date_to_datetime(date_dow)

        return Video(header, desc, datetime_date_dow, "")
