from typing import Any, AsyncIterator, Iterator
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

from ordis_rag.wiki.wiki_parser import WikiParser


def _build_metadata(soup: Any, url: str) -> dict:
    """Build metadata from BeautifulSoup output."""
    metadata = {"source": url}
    if title := soup.find("title"):
        metadata["title"] = title.get_text()
    if description := soup.find("meta", attrs={"name": "description"}):
        metadata["description"] = description.get("content", "No description found.")
    if html := soup.find("html"):
        metadata["language"] = html.get("lang", "No language found.")
    return metadata

class WikiLoader(WebBaseLoader):
    def __init__(self, web_path = "", header_template = None, verify_ssl = True, proxies = None, continue_on_failure = False, autoset_encoding = True, encoding = None, web_paths = ..., requests_per_second = 2, default_parser = "html.parser", requests_kwargs = None, raise_for_status = False, bs_get_text_kwargs = None, bs_kwargs = None, session = None, *, show_progress = True, trust_env = False):
        super().__init__(web_path, header_template, verify_ssl, proxies, continue_on_failure, autoset_encoding, encoding, web_paths, requests_per_second, default_parser, requests_kwargs, raise_for_status, bs_get_text_kwargs, bs_kwargs, session, show_progress=show_progress, trust_env=trust_env)
        self.parser = WikiParser()


    def lazy_load(self) -> Iterator[Document]:
        """Lazy load text from the url(s) in web_path."""
        for path in self.web_paths:
            soup = self._scrape(path, bs_kwargs=self.bs_kwargs)
            text = self.parser.parse_soup(soup)
            metadata = _build_metadata(soup, path)
            yield Document(page_content=text, metadata=metadata)


    async def alazy_load(self) -> AsyncIterator[Document]:
        """Async lazy load text from the url(s) in web_path."""
        results = await self.ascrape_all(self.web_paths)
        for path, soup in zip(self.web_paths, results):
            text = self.parser.parse_soup(soup)
            metadata = _build_metadata(soup, path)
            yield Document(page_content=text, metadata=metadata)
