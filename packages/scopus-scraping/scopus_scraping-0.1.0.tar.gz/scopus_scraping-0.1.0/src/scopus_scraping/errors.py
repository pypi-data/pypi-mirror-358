from dataclasses import dataclass


@dataclass(eq=False, kw_only=True)
class ScopusScrapingError(Exception):
    @property
    def message(self) -> str:
        return "Scopus scraping unknown error"


@dataclass(eq=False, kw_only=True)
class ScopusPageNotFoundError(ScopusScrapingError):
    @property
    def message(self) -> str:
        return "Scopus work not found"
