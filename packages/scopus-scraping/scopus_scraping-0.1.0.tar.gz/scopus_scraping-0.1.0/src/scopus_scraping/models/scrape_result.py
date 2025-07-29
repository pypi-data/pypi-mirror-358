from pydantic import BaseModel, Field

from scopus_scraping.models.records import ScopusCitations


class ScrapeResult[T](BaseModel):
    result: ScopusCitations = Field(
        description="",
        examples=[],
    )
    scrapper_data: T | None = Field(
        default=None,
        description="",
        examples=[],
    )
