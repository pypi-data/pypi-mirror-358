import functools

import httpx
import pydantic

from orcid_scraping.logger import logger
from orcid_scraping.models.orcid import Orcid
from orcid_scraping.models.researcher.work import OrcidResearcherWork
from orcid_scraping.models.researcher.work_url import OrcidResearcherWorkUrlBuilder
from orcid_scraping.tools.base import OrcidScrapeTool

from .models import (
    ApiScrapeResult,
    ApiScrapeResultData,
    WorkInfo,
    WorksExtendedPage,
)


class OrcidScrapeToolApi(OrcidScrapeTool):
    _httpx_client: httpx.Client = httpx.Client(
        follow_redirects=True,
    )

    @pydantic.validate_call(validate_return=True)
    def scrape_works(
        self,
        orcid: Orcid,
    ) -> ApiScrapeResult:
        """
        Scrape all works from an ORCID profile.

        Workflow:
        1. Retrieves paginated work data
        2. Extracts basic work information
        3. Fetches extended metadata for each work
        4. Converts to simplified researcher work format

        Args:
            orcid: Researcher's ORCID identifier (e.g., "0000-0002-1825-0097")

        Returns:
            ApiScrapeResult: Contains:
                - works: Simplified researcher works ready for consumption
                - scraper_data: Raw scraping metadata for debugging

        Raises:
            OrcidScrapeToolOrcidNotFoundError: For invalid/missing ORCID IDs
            OrcidScrapeToolWorkNotFoundError: When works can't be retrieved

        """
        work_extended_pages = self._get_works_extended_pages(orcid)
        work_infos = self._extract_work_infos(work_extended_pages)
        work_infos = self._get_extended_work_infos(
            orcid=orcid,
            work_infos=work_infos,
        )
        researcher_works = []
        for work_info in work_infos:
            url = None
            if work_info.url:
                url = OrcidResearcherWorkUrlBuilder.create(url=work_info.url.value)
            journal_title = None
            if work_info.journal_title:
                journal_title = work_info.journal_title.value
            researcher_work = OrcidResearcherWork(
                journal_title=journal_title,
                title=work_info.title.value,
                url=url,
            )
            researcher_works.append(researcher_work)
        return ApiScrapeResult(
            works=researcher_works,
            scraper_data=ApiScrapeResultData(
                pages=work_extended_pages,
                works=work_infos,
            ),
        )

    @pydantic.validate_call(validate_return=True)
    def _get_extended_work_infos(
        self,
        orcid: Orcid,
        work_infos: list[WorkInfo],
    ) -> list[WorkInfo]:
        """
        Enhances basic work information with full metadata from ORCID.

        Iterates through initial work summaries and fetches complete details
        using each work's unique put code.

        Args:
            orcid: Researcher's ORCID identifier
            work_infos: List of basic work summaries from initial scrape

        Returns:
            List of enriched WorkInfo objects with full metadata

        """
        extended_work_infos = []
        for work_info in work_infos:
            logger.debug(work_info)
            extended_work_info = self._get_work_info(
                orcid=orcid,
                work_id=int(work_info.put_code.value),
            )
            extended_work_infos.append(extended_work_info)
        logger.debug(extended_work_infos)
        return extended_work_infos

    @pydantic.validate_call(validate_return=True)
    def _extract_work_infos(
        self,
        work_extended_pages: list[WorksExtendedPage],
    ) -> list[WorkInfo]:
        """
        Flattens paginated work data into a single list of work summaries.

        Processes ORCID's grouped response structure by extracting individual
        works from all group containers across all pages.

        Args:
            work_extended_pages: List of paginated work group responses

        Returns:
            Consolidated list of all work summaries

        """
        work_infos = []
        for work_extended_page in work_extended_pages:
            for group in work_extended_page.groups:
                work_infos.extend(group.works)
        return work_infos

    @pydantic.validate_call(validate_return=True)
    def _get_work_infos(
        self,
        orcid: Orcid,
        work_ids: list[pydantic.PositiveInt],
    ) -> list[WorkInfo]:
        """
        Batch fetches detailed metadata for specific work IDs.

        Args:
            orcid: Researcher's ORCID identifier
            work_ids: List of work put codes to retrieve

        Returns:
            List of detailed WorkInfo objects for requested IDs

        """
        work_infos = []
        get_work_info = functools.partial(
            self._get_work_info,
            orcid=orcid,
        )
        for work_id in work_ids:
            work_info = get_work_info(work_id=work_id)
            work_infos.append(work_info)
        return work_infos

    @pydantic.validate_call(validate_return=True)
    def _get_work_info(self, orcid: Orcid, work_id: pydantic.PositiveInt) -> WorkInfo:
        """
        Fetch detailed metadata for a single work by put code.

        Endpoint: https://orcid.org/{orcid}/getWorkInfo.json

        Args:
            orcid: Researcher's ORCID identifier
            work_id: Unique put code identifier for the work

        Returns:
            WorkInfo: Parsed JSON response containing full work metadata

        Raises:
            OrcidScrapeToolWorkNotFoundError: For invalid/missing work IDs

        """
        url = rf"https://orcid.org/{orcid}/getWorkInfo.json"
        params = {"workId": work_id}
        response = self._httpx_client.get(
            url=url,
            params=params,
        )
        return response.json()

    @pydantic.validate_call(validate_return=True)
    def _get_works_extended_page(
        self,
        orcid: Orcid,
        offset: pydantic.NonNegativeInt,
        page_size: pydantic.PositiveInt,
    ) -> WorksExtendedPage:
        """
        Fetch a single paginated works page from ORCID API.

        Endpoint: https://orcid.org/{orcid}/worksExtendedPage.json

        Args:
            orcid: Researcher's ORCID identifier
            offset: Pagination starting index (0-based)
            page_size: Number of items per page (max 100)

        Return:
            WorksExtendedPage: Parsed JSON response for the requested page

        Raise:
            OrcidScrapeToolOrcidNotFoundError: For invalid ORCID IDs

        """
        url = rf"https://orcid.org/{orcid}/worksExtendedPage.json"
        params = {
            "offset": offset,
            "sort": "date",
            "sortAsc": False,
            "pageSize": page_size,
        }
        return self._httpx_client.get(
            url=url,
            params=params,
        ).json()

    @pydantic.validate_call(validate_return=True)
    def _get_works_extended_pages(self, orcid: Orcid) -> list[WorksExtendedPage]:
        """
        Retrieve all paginated work pages for an ORCID profile.

        Automatically handles pagination by:
        1. Fetching initial page (offset=0)
        2. Continuing until next_offset >= total_groups
        3. Using consistent page size (50)

        Args:
            orcid: Researcher's ORCID identifier

        Returns:
            List of all worksExtendedPage responses for complete profile

        """
        offset = 0
        page_size = 50
        get_works_extended_page = functools.partial(
            self._get_works_extended_page,
            orcid=orcid,
            page_size=page_size,
        )
        last_response = get_works_extended_page(offset=offset)
        responses = [last_response]
        while last_response.total_groups > last_response.next_offset:
            offset = last_response.next_offset
            last_response = get_works_extended_page(offset=offset)
            responses.append(last_response)
        return responses
