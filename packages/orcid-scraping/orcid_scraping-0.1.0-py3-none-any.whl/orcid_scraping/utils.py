import re

from orcid_scraping.errors import OrcidInvalidFormatError


def sanitize_orcid(orcid: str) -> str:
    """
    Validate and normalizes an ORCID identifier string.

    Parses input string to extract the standard ORCID format, handling both
    the standalone ID and URL formats. The function:
    - Accepts both full URLs (https://orcid.org/XXXX-...) and bare IDs
    - Validates the ORCID format according to the official pattern
    - Returns a normalized ORCID string in the format XXXX-XXXX-XXXX-XXXX
    - Handles the final character which can be a digit or 'X'

    Args:
        orcid: The ORCID string to validate. Can be either:
                - The full ORCID URL (https://orcid.org/0000-0000-0000-0000)
                - The bare ORCID ID (0000-0000-0000-0000)

    Returns:
        The normalized ORCID ID in standard format (without URL prefix)

    Raises:
        OrcidInvalidFormatError: If input:
            - Is not a string
            - Doesn't match the ORCID pattern
            - Has incorrect segment lengths or invalid characters

    Examples:
        Valid inputs:
            validate_orcid("https://orcid.org/0000-0001-2345-6789")
            -> "0000-0001-2345-6789"

            validate_orcid("0000-0002-3456-789X")
            -> "0000-0002-3456-789X"

        Invalid inputs:
            validate_orcid("0000-000-1234-5678")   # Too short segment
            validate_orcid("0000000123456789")      # No hyphens
            validate_orcid(1234567890)              # Non-string input

    """
    if isinstance(orcid, str):
        match = re.fullmatch(
            r"(?:(?:https?://)?orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[\dX])",
            orcid,
            flags=re.IGNORECASE,
        )
        if match:
            return str(match.group(1))
    raise OrcidInvalidFormatError(orcid=orcid)
