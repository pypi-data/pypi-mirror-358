from pydantic import BaseModel, Field

from orcid_scraping.models.researcher.work import OrcidResearcherWork


class ScrapeResult[T](BaseModel):
    """
    Container for the results of an ORCID researcher profile scraping operation.

    This generic class encapsulates both the extracted scholarly works and optional
    scraper-specific metadata. It serves as the standard return type for ORCID scraping
    functions and methods.

    Type Parameters:
        T: The type of scraper-specific metadata (e.g., raw API response,
        pagination details, or processing statistics)
    """

    works: list[OrcidResearcherWork] = Field(
        description="List of scholarly works extracted from the researcher's ORCID profile",
        examples=[
            [
                {
                    "title": (
                        "Comparative analysis of parallel discrete event simulation algorithms"
                    ),
                    "url": "https://doi.org/10.1117/12.3060495",
                },
                {
                    "title": "Generalized Lyapunov Matrix Model for Stability Analysis",
                    "url": "https://doi.org/10.2139/ssrn.5087186",
                },
            ],
        ],
    )
    scraper_data: T | None = Field(
        default=None,
        description=(
            "Optional container for scraper-specific metadata and intermediate processing data"
        ),
        examples=[
            {"api_version": "3.0", "response_time_ms": 245, "pages_scraped": 3},
            {"html_source_hash": "a1b2c3d4e5", "scrape_timestamp": "2023-10-15T08:30:00Z"},
            {"pagination": {"next_offset": 50, "total_groups": 21}},
        ],
    )
