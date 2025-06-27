

from typing import Set
from pydantic import BaseModel

class CrawlerLink(BaseModel):
    url: str
    title: str

    def __hash__(self):
        return hash(self.url)

class CrawlerLinks(BaseModel):
    to_crawl: Set[str]
    links: Set[CrawlerLink]