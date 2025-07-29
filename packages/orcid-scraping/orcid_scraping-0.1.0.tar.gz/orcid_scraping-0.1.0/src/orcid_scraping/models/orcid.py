import typing

import pydantic

from orcid_scraping.utils import sanitize_orcid


type Orcid = typing.Annotated[str, pydantic.AfterValidator(sanitize_orcid)]
