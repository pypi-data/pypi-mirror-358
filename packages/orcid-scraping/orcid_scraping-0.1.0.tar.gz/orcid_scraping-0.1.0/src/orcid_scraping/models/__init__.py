from .orcid import Orcid
from .researcher.work import OrcidResearcherWork
from .researcher.work_url import (
    OrcidResearcherWorkUrlBase,
    OrcidResearcherWorkUrlBuilder,
    OrcidResearcherWorkUrlScopus,
    OrcidResearcherWorkUrlSite,
    OrcidResearcherWorkUrlUnknowm,
)
from .scrape_result import ScrapeResult


__all__ = [
    "Orcid",
    "OrcidResearcherWork",
    "OrcidResearcherWorkUrlBase",
    "OrcidResearcherWorkUrlBuilder",
    "OrcidResearcherWorkUrlScopus",
    "OrcidResearcherWorkUrlSite",
    "OrcidResearcherWorkUrlUnknowm",
    "ScrapeResult",
]
