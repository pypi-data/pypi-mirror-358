from pydantic import BaseModel, Field

from orcid_scraping.models.researcher.work_url import (
    OrcidResearcherWorkUrlBase,
)


class OrcidResearcherWork(BaseModel):
    """
    Represents a scholarly work associated with an ORCID researcher profile.

    This model captures essential metadata about research outputs listed in an ORCID record,
    including publications, conference papers, and other academic contributions.
    """

    journal_title: str | None = Field(
        default=None,
        description="",
        examples=[],
    )
    title: str = Field(
        description="The full title of the scholarly work as listed in the ORCID record",
        examples=[
            (
                "Comparative analysis of parallel discrete event simulation algorithms: "
                "Time Warp, Window Racer, and Null Messages"
            ),
            (
                "Generalized Lyapunov Matrix Model for "
                "Stability Analysis of Nonlinear Time-Varying Systems"
            ),
            "Disk Space Management Automation with CSI and Kubernetes",
        ],
    )
    url: OrcidResearcherWorkUrlBase | None = Field(
        default=None,
        description=(
            "Direct access URL to the full work content, typically a DOI link or publisher URL"
        ),
        examples=[
            "https://doi.org/10.1117/12.3060495",
            "https://doi.org/10.2139/ssrn.5087186",
            "https://www.worldcat.org/isbn/9789813366312",
        ],
    )
