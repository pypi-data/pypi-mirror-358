import pydantic
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.wait import WebDriverWait

from orcid_scraping.models import (
    Orcid,
    OrcidResearcherWork,
    OrcidResearcherWorkUrlBuilder,
)
from orcid_scraping.tools.base import OrcidScrapeTool

from .models import SeleniumScrapeResult


AFTER_COOKIE_ACCEPT_WAIT_TIME = 3
WAIT_TIME = 15
SCOPUS_URL_WAIT_TIME = 1


class OrcidScrapeToolSelenium(OrcidScrapeTool):
    _driver: WebDriver

    def __init__(self, driver: WebDriver):
        self._driver = driver
        super().__init__()

    @pydantic.validate_call(validate_return=True)
    def scrape_works(self, orcid: Orcid) -> SeleniumScrapeResult:
        return SeleniumScrapeResult(
            works=self._get_works(
                driver=self._driver,
                orcids=[orcid],
            )[0],
        )

    @classmethod
    def _get_works(
        cls,
        driver: WebDriver,
        orcids: list[Orcid],
    ) -> list[list[OrcidResearcherWork]]:
        orcid_works = []
        for orcid_id in orcids:
            works = OrcidScrapeToolSelenium._get_works_for_orcid(driver, orcid_id)
            orcid_works.append(works)
        return orcid_works

    @classmethod
    def _get_works_for_orcid(
        cls,
        driver: WebDriver,
        orcid: Orcid,
    ) -> list[OrcidResearcherWork]:
        driver.get(cls.get_orcid_url(orcid))
        OrcidScrapeToolSelenium._click_to_accept_cookies(driver)
        works_we = OrcidScrapeToolSelenium._get_works_we(driver)
        works = []
        for work_we in works_we:
            work = OrcidScrapeToolSelenium._work_we_to_work(driver, work_we)
            works.append(work)
        return works

    @classmethod
    def get_orcid_url(cls, orcid: Orcid) -> str:
        return f"https://orcid.org/{orcid}"

    @classmethod
    def _work_we_to_work(
        cls,
        driver: WebDriver,
        work: WebElement,
    ) -> OrcidResearcherWork:
        title = work.find_element(
            By.XPATH,
            ".//h4[@class='work-title orc-font-body ng-star-inserted']",
        ).text
        url = None
        try:
            url = OrcidScrapeToolSelenium._get_link(driver, work)
        except NoSuchElementException:
            pass
        else:
            url = OrcidResearcherWorkUrlBuilder.create(url=url)
        return OrcidResearcherWork(
            title=title,
            url=url,
        )

    @classmethod
    def _get_works_we(
        cls,
        driver: WebDriver,
    ) -> list[WebElement]:
        WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.ID, "works")))
        return driver.find_elements(By.TAG_NAME, "app-work-stack")

    @classmethod
    def _get_link(
        cls,
        driver: WebDriver,
        work: WebElement,
    ) -> pydantic.HttpUrl:
        show_more_button = work.find_element(
            By.XPATH,
            ".//a[@role='button'][contains(text(), 'Show more detail')]",
        )
        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
        show_more_button.click()
        scopus_bv = (
            By.XPATH,
            ".//app-display-attribute//a[contains(text(), 'www.scopus.com')]",
        )
        scopus_we = None
        try:
            scopus_we = WebDriverWait(work, SCOPUS_URL_WAIT_TIME).until(
                EC.presence_of_element_located(scopus_bv),
            )
        except TimeoutException:
            scopus_we = work.find_element(*scopus_bv)
        scopus_url = scopus_we.text.strip()
        return pydantic.HttpUrl(scopus_url)

    @classmethod
    def _click_to_accept_cookies(
        cls,
        driver: WebDriver,
    ) -> None:
        btn_xpath = "//button[contains(text(), 'Reject Unnecessary Cookies')]"
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, btn_xpath)),
        )
        cookie_btn = driver.find_element(By.XPATH, btn_xpath)
        cookie_btn.click()
        # WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "//div[@class='onetrust-pc-dark-filter ot-fade-in'][contains(@style, 'display: none;')]")))
        cookie_banner_xpath = (
            "//div[@aria-label='Cookie banner'][contains(@style, 'display: none;')]"
        )
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, cookie_banner_xpath)),
        )

    @classmethod
    def _click_show_citation(
        cls,
        driver: WebDriver,
        work: WebElement,
    ) -> None:
        show_cit_btn_xpath = ".//a[@role='button'][normalize-space()='Show citation']"
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, show_cit_btn_xpath)),
        )
        show_cit_btn = work.find_element(By.XPATH, show_cit_btn_xpath)
        driver.execute_script("arguments[0].scrollIntoView();", show_cit_btn)
        show_cit_btn.click()

    @classmethod
    def scroll_to_elem(
        cls,
        driver: WebDriver,
        elem: WebElement,
    ) -> None:
        driver.execute_script("arguments[0].scrollIntoView();", elem)
