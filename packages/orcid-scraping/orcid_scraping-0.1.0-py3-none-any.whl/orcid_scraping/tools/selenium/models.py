from pydantic import BaseModel, Field

from orcid_scraping.models.scrape_result import ScrapeResult


class SeleniumScrapeResultData(BaseModel): ...


class SeleniumScrapeResult(ScrapeResult[SeleniumScrapeResultData]): ...
