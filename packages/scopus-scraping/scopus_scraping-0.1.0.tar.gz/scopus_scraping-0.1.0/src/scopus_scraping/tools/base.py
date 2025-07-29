import abc

from scopus_scraping.models.scopus_citations_url import ScopusCitationsUrl
from scopus_scraping.models.scrape_result import ScrapeResult


class ScopusScrapeTool(abc.ABC):
    @abc.abstractmethod
    def scrape_citations(
        self,
        url: ScopusCitationsUrl,
    ) -> ScrapeResult: ...


class ScopusScrapeToolAsync(abc.ABC):
    @abc.abstractmethod
    async def scrape_works(
        self,
        url: ScopusCitationsUrl,
    ) -> ScrapeResult: ...
