from abc import ABC, abstractmethod

import pydantic

from orcid_scraping.models.orcid import Orcid
from orcid_scraping.models.scrape_result import ScrapeResult


class OrcidScrapeTool(ABC):
    @abstractmethod
    def scrape_works(
        self,
        orcid: Orcid,
    ) -> ScrapeResult: ...


class OrcidScrapeAsyncTool(ABC):
    @abstractmethod
    async def scrape_works(
        self,
        orcid: Orcid,
    ) -> ScrapeResult: ...
