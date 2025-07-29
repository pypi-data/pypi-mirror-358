import pydantic
from pydantic import BaseModel, Field

from scopus_scraping.models.scrape_result import ScrapeResult


class SeleniumScrapperData(BaseModel):
    """SeleniumScrapperData"""


class SeleniumScrapeResult(ScrapeResult[SeleniumScrapperData]): ...
