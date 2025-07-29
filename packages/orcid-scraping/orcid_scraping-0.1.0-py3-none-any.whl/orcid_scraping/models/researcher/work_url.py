import abc
import enum
import re
import typing

import pydantic
from pydantic import BaseModel, Field


class OrcidResearcherWorkUrlSite(enum.StrEnum):
    SCOPUS = "scopus"


class OrcidResearcherWorkUrlBase(BaseModel):
    source: OrcidResearcherWorkUrlSite | None = Field(
        default=None,
        description="",
        examples=[],
    )
    value: pydantic.HttpUrl = Field(
        description="",
        examples=[],
    )

    @classmethod
    @abc.abstractmethod
    def is_valid_url(cls, url: pydantic.HttpUrl) -> bool: ...

    @pydantic.model_validator(mode="after")
    def validate_url_value(self) -> typing.Self:
        if self.is_valid_url(self.value) is False:
            raise ValueError
        return self


class OrcidResearcherWorkUrlUnknowm(OrcidResearcherWorkUrlBase):
    source: None = None

    @classmethod
    @pydantic.validate_call(validate_return=True)
    def is_valid_url(cls, _: pydantic.HttpUrl) -> bool:
        return True


class OrcidResearcherWorkUrlScopus(OrcidResearcherWorkUrlBase):
    source: OrcidResearcherWorkUrlSite = OrcidResearcherWorkUrlSite.SCOPUS

    @classmethod
    @pydantic.validate_call(validate_return=True)
    def is_valid_url(cls, url: pydantic.HttpUrl) -> bool:
        pattern = (
            r"^http:\/\/www\.scopus\.com\/inward\/record\.url\?eid=2-s2\.0-\d+&partnerID=[A-Z0-9]+$"
        )
        return bool(re.fullmatch(pattern, str(url)))


class OrcidResearcherWorkUrlBuilder:
    registry: typing.ClassVar[list[type[OrcidResearcherWorkUrlBase]]] = [
        OrcidResearcherWorkUrlScopus,
    ]

    @classmethod
    @pydantic.validate_call(validate_return=True)
    def create(cls, url: pydantic.HttpUrl) -> OrcidResearcherWorkUrlBase:
        work_url = OrcidResearcherWorkUrlUnknowm(value=url)
        for url_type in OrcidResearcherWorkUrlBuilder.registry:
            if url_type.is_valid_url(url) is True:
                work_url = url_type(value=url)
                break
        return work_url
