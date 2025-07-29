import re

import pydantic
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.wait import WebDriverWait

from scopus_scraping.logger import logger
from scopus_scraping.models import ScopusCitation, ScopusCitations
from scopus_scraping.models.scopus_citations_url import ScopusCitationsUrl
from scopus_scraping.tools.base import ScopusScrapeTool

from .models import SeleniumScrapeResult


MAX_WAIT_TIME = 5


class ScopusScrapeToolSelenium(ScopusScrapeTool):
    _selenium_driver: WebDriver

    def __init__(
        self,
        driver: WebDriver,
    ):
        self._selenium_driver = driver

    @pydantic.validate_call(validate_return=True)
    def scrape_citations(self, url: ScopusCitationsUrl) -> SeleniumScrapeResult:
        records = self._get_citations_batched(
            driver=self._selenium_driver,
            urls=[url],
        )
        return SeleniumScrapeResult(
            result=records[0],
        )

    @staticmethod
    def _get_citations_batched(
        driver: WebDriver,
        urls: list[ScopusCitationsUrl],
    ) -> list[ScopusCitations]:
        citations_batched = []
        for url in urls:
            driver.get(str(url))
            citations = []
            count = ScopusScrapeToolSelenium._get_citations_count(driver)
            citations = []
            if count > 0:
                citations = ScopusScrapeToolSelenium._get_citations(driver)
            scopus_citations = ScopusCitations(
                url=url,
                count=len(citations),
                total=count,
                citations=citations,
            )
            citations_batched.append(scopus_citations)
        return citations_batched

    @staticmethod
    def _get_citations(
        driver: WebDriver,
    ) -> list[ScopusCitation]:
        records_we_locator = (By.XPATH, ".//div[@class='recordPageBoxItem']")
        try:
            wait = WebDriverWait(driver, MAX_WAIT_TIME)
            wait.until(
                EC.presence_of_all_elements_located(records_we_locator),
            )
        except TimeoutException as err:
            logger.warning(err)
        records_we = driver.find_elements(*records_we_locator)
        return list(map(ScopusScrapeToolSelenium._parse_record_we, records_we))

    @staticmethod
    def _get_citations_count(driver: WebDriver) -> pydantic.NonNegativeInt:
        records_we_locator = (By.XPATH, "//div[@id='recordPageBoxes']//h3[@class='panel-title']")
        try:
            wait = WebDriverWait(driver, MAX_WAIT_TIME)
            records_we = wait.until(
                lambda d: d.find_element(*records_we_locator).text.strip() != "",
            )
        except TimeoutException as err:
            logger.warning(err)
        records_we = driver.find_element(*records_we_locator)
        count = records_we.text
        logger.debug(count)
        count = re.search(r"\d+", count).group()
        return pydantic.NonNegativeInt(count)

    @staticmethod
    def _parse_record_we(record_we: WebElement) -> ScopusCitation:
        authors_locator = (By.XPATH, "*")
        authors, _, title, _, journal_title = record_we.find_elements(*authors_locator)
        authors = authors.find_elements(*authors_locator)
        authors = [author.text.strip() for author in authors]
        title = title.text
        journal_title = journal_title.text
        return ScopusCitation(
            journal_title=journal_title,
            title=title,
            authors=authors,
        )
