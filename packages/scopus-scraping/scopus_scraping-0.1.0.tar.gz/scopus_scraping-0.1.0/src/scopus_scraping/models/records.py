import pydantic
from pydantic import BaseModel, Field

from scopus_scraping.models.scopus_citations_url import ScopusCitationsUrl


class ScopusCitation(BaseModel):
    journal_title: str | None = Field(
        default=None,
        description="",
        examples=[],
    )
    title: str = Field(
        description="",
        examples=[],
    )
    authors: list[str] | None = Field(
        default=None,
        description="",
        examples=[],
    )


class ScopusCitations(BaseModel):
    url: ScopusCitationsUrl = Field(
        description="",
        examples=[],
    )
    count: pydantic.NonNegativeInt = Field(
        description="",
        examples=[],
    )
    total: pydantic.NonNegativeInt = Field(
        description="",
        examples=[],
    )
    citations: list[ScopusCitation] = Field(
        description="",
        examples=[],
    )
