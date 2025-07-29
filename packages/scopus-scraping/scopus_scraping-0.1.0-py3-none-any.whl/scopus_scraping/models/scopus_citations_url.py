import typing

import pydantic

from scopus_scraping.utils import sanitize_scopus_url


type ScopusCitationsUrl = typing.Annotated[pydantic.HttpUrl, sanitize_scopus_url]
