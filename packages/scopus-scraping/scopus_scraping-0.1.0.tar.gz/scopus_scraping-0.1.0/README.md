# Scopus scraping

Scrape citations from Scopus.

**For now only supports links like `http://www.scopus.com/inward/record.url?eid=2-s2.0-85147250183&partnerID=MN8TOARS` from ORCID pages**

## Getting started

### Pre-requisites

1. Python >= 3.13

### Installation

1. pip: ```pip install scopus-scraping```

2. uv: ```uv add scopus-scraping```

I would also recommend install [orcid-scraping](https://github.com/Tolyan3k/orcid_scraping)
library for better bypassing the Cloudflare Anti-bot filter.

Maybe I'll add some bypass filters at some day.

## Example usage

Here's an example usage with [orcid-scraping](https://github.com/Tolyan3k/orcid_scraping) library in tandem:

```python
import secrets
import time
from pprint import pprint

from orcid_scraping.models import OrcidResearcherWorkUrlSite
from orcid_scraping.tools.selenium import OrcidScrapeToolSelenium
from selenium.webdriver import Chrome, ChromeOptions

from scopus_scraping.tools.selenium import ScopusScrapeToolSelenium


driver_opts = ChromeOptions()
driver = Chrome(options=driver_opts)
try:
    orcid_scrape_tool = OrcidScrapeToolSelenium(driver=driver)
    scopus_scrape_tool = ScopusScrapeToolSelenium(driver=driver)

    orcid = "https://orcid.org/0000-0003-0198-1886"
    orcid_scrape_result = orcid_scrape_tool.scrape_works(orcid=orcid)
    for work in orcid_scrape_result.works:
        if work.url is not None and work.url.source == OrcidResearcherWorkUrlSite.SCOPUS:
            time.sleep(secrets.randbelow(3))
            citation = scopus_scrape_tool.scrape_citations(url=str(work.url.value))
            pprint(citation)
finally:
    driver.quit()
```
