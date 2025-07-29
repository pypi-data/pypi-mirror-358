import pydantic
from pydantic import BaseModel, Field

from orcid_scraping.models.scrape_result import ScrapeResult


class ApiScrapeResultData(BaseModel):
    """Container for scraped ORCID works data including pagination information and works list."""

    pages: list["WorksExtendedPage"] = Field(
        description="List of paginated result pages containing grouped works",
    )
    works: list["WorkInfo"] = Field(
        description="Flattened list of all works across all pages",
    )


class ApiScrapeResult(ScrapeResult[ApiScrapeResultData]):
    """Scrape result container specifically for ORCID works API data"""


class WorkInfoJournalTitle(BaseModel):
    """Journal title information for a work"""

    value: str = Field(
        alias="value",
        description="The full title of the journal where the work was published",
    )


class WorkInfoTitle(BaseModel):
    """Title information for a work"""

    value: str = Field(
        alias="value",
        description="The main title of the scholarly work",
    )


class WorkInfoWorkType(BaseModel):
    """Work type classification"""

    value: str = Field(
        alias="value",
        description="Type of work (e.g., 'journal-article', 'conference-paper')",
    )


class WorkInfoPutCode(BaseModel):
    """ORCID system identifier for a work"""

    value: str = Field(
        alias="value",
        description="Unique identifier for the work in the ORCID system",
    )


class WorkInfoUrl(BaseModel):
    """URL associated with the work"""

    value: pydantic.HttpUrl = Field(
        alias="value",
        description="Direct URL to access the work online, if available",
    )


class WorkInfo(BaseModel):
    """Detailed information about a scholarly work"""

    put_code: WorkInfoPutCode = Field(
        alias="putCode",
        description="ORCID's unique identifier for this work",
    )
    journal_title: WorkInfoJournalTitle | None = Field(
        alias="journalTitle",
        description="Journal or publication venue where the work appeared",
    )
    number_of_contributors: pydantic.NonNegativeInt = Field(
        alias="numberOfContributors",
        description="Total count of contributors associated with this work",
    )
    source: str = Field(
        alias="source",
        description="ORCID identifier of the organization claiming the work",
    )
    source_name: str = Field(
        alias="sourceName",
        description="Name of the organization that asserted this work",
    )
    title: WorkInfoTitle = Field(
        alias="title",
        description="Title of the scholarly work",
    )
    work_type: WorkInfoWorkType = Field(
        alias="workType",
        description="Categorization of the work type",
    )
    url: WorkInfoUrl | None = Field(
        alias="url",
        description="Web-accessible location for the full work",
    )


class WorksExtendedPageGroupWork(WorkInfo):
    """Work information within a group (alias for WorkInfo)"""


class WorksExtendedPageGroup(BaseModel):
    """Container for a group of related works"""

    active_put_code: int = Field(
        alias="activePutCode",
        description="Identifier of the currently active version of this work group",
    )
    default_put_code: int = Field(
        alias="defaultPutCode",
        description="Identifier of the default version of this work group",
    )
    group_id: int = Field(
        alias="groupId",
        description="Unique identifier for this group of work versions",
    )
    works: list[WorksExtendedPageGroupWork] = Field(
        alias="works",
        description="List of different versions/variants of this work",
    )


class WorksExtendedPage(BaseModel):
    """Paginated result set from ORCID works API"""

    next_offset: pydantic.PositiveInt = Field(
        alias="nextOffset",
        description="Offset value to request the next page of results",
    )
    total_groups: pydantic.NonNegativeInt = Field(
        alias="totalGroups",
        description="Total number of work groups across all pages",
    )
    groups: list[WorksExtendedPageGroup] = Field(
        alias="groups",
        description="Work groups contained in this page of results",
    )
