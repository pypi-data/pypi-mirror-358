from dataclasses import dataclass


@dataclass(eq=False, kw_only=True)
class OrcidScrapeToolError(Exception):
    """
    Base exception class for all ORCID Scrape Tool errors.

    This exception combines Pydantic model capabilities with Python exception handling,
    serving as the foundation for all custom exceptions in the ORCID scraping tool.
    It provides a default error message and can be extended with additional fields.

    Attributes:
        message: Computed property providing a default error description.

    """

    @property
    def message(self) -> str:
        """
        Returns the default error message for base ORCID scraping errors.

        This computed field provides a consistent message format for all derived exceptions
        unless overridden. The default message indicates an unspecified error occurred.

        Returns:
            str: The static error message 'Unknown error'

        """
        return "OrcidScrapeToolError Unknown error"


@dataclass(eq=False, kw_only=True)
class OrcidInvalidFormatError(ValueError, OrcidScrapeToolError):
    """
    Exception raised when an ORCID identifier format is invalid.

    This error indicates a problem with the ORCID string format, including:
    - Incorrect length or segment structure
    - Invalid characters
    - Missing hyphens
    - Improper URL formatting

    Inherits from both ValueError and OrcidScrapeToolError to support:
    - Standard value error handling
    - Custom tool exception hierarchy

    Attributes:
        orcid: The invalid ORCID string that caused the error
        message: Computed property describing the specific format error

    """

    orcid: str

    @property
    def message(self) -> str:
        """
        Generates a contextual error message including the invalid ORCID.

        Computes a message that incorporates the problematic ORCID string,
        providing immediate context about what caused the validation failure.

        Returns:
            str: Formatted error message showing the invalid ORCID

        """
        return f"Invalid ORCID format: '{self.orcid}'"


@dataclass(eq=False, kw_only=True)
class OrcidNotFoundError(OrcidScrapeToolError):
    """
    Exception raised when a requested ORCID record cannot be found.

    Indicates that the specified ORCID doesn't exist in the ORCID registry,
    or isn't accessible due to privacy settings or deletion.

    Attributes:
        orcid: The ORCID identifier that couldn't be located
        message: Computed property describing the lookup failure

    """

    orcid: str

    @property
    def message(self) -> str:
        """
        Generates a contextual error message for missing ORCID records.

        Provides a formatted message that includes the specific ORCID ID
        that couldn't be found, helping with debugging and error reporting.

        Returns:
            str: Formatted error message showing the missing ORCID

        """
        return f"ORCID '{self.orcid}' not found"


@dataclass(eq=False, kw_only=True)
class WorkNotFoundError(OrcidScrapeToolError):
    """
    Exception raised when a specific work cannot be found in an ORCID record.

    Indicates that the requested work (publication) doesn't exist in the
    specified ORCID profile, or isn't accessible due to visibility settings.

    Attributes:
        orcid: The ORCID identifier where the work was searched
        work_id: The work put code that couldn't be located
        message: Computed property describing the missing work

    """

    orcid: str
    work_id: int  # ORCID's positive integer put code

    @property
    def message(self) -> str:
        """
        Generates a contextual error message for missing works.

        Provides a formatted message that includes both the ORCID ID and
        the specific work put code that couldn't be found, enabling precise
        identification of the missing item.

        Returns:
            str: Formatted error message showing both ORCID and work ID

        """
        return f"Work with id '{self.work_id}' for ORCID '{self.orcid}' not found"
