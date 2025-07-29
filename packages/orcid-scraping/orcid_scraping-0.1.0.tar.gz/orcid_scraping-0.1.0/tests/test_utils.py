import pytest

from orcid_scraping.errors import OrcidInvalidFormatError
from orcid_scraping.utils import sanitize_orcid


# Valid ORCID test cases with different formats
@pytest.mark.parametrize(
    ("input_orcid", "expected"),
    [
        # Standard formats
        ("0000-0001-2345-6789", "0000-0001-2345-6789"),
        ("0000-0002-3456-789X", "0000-0002-3456-789X"),
        # URL formats
        ("https://orcid.org/0000-0003-4567-7890", "0000-0003-4567-7890"),
        ("http://orcid.org/0000-0004-5678-890X", "0000-0004-5678-890X"),
        ("orcid.org/0000-0005-6789-9012", "0000-0005-6789-9012"),
        # Case variations
        ("HTTPS://ORCID.ORG/0000-0006-7890-1234", "0000-0006-7890-1234"),
    ],
)
def test_valid_orcid_formats(input_orcid, expected):
    """Test various valid ORCID formats are correctly normalized."""
    assert sanitize_orcid(input_orcid) == expected


# Invalid ORCID test cases
@pytest.mark.parametrize(
    "invalid_orcid",
    [
        # Format violations
        "0000-000-1234-5678",  # Too short segment
        "0000-00012-3456-789",  # Segment length mismatch
        "00000000123456789",  # No hyphens
        "0000-0001-2345-678",  # Last segment too short
        "0000-0001-2345-67890",  # Last segment too long
        "0000-0001-2345-678Y",  # Invalid character in checksum
        # URL format issues
        "https://example.org/0000-0001-2345-6789",  # Wrong domain
        "ftp://orcid.org/0000-0001-2345-6789",  # Wrong protocol
        "https://orcid.org/0000-0001-2345-6789/",  # Trailing slash
        "https://orcid.org/0000-0001-2345-6789/extra",  # Extra path
        # Structural issues
        "0000-0001-2345-6789 ",  # Trailing space
        " 0000-0001-2345-6789",  # Leading space
        "0000 -0001-2345-6789",  # Space in ID
        # Type errors
        1234567890,  # Integer input
        None,  # None input
        ["0000-0001-2345-6789"],  # List input
        {"orcid": "0000-0001-2345-6789"},  # Dict input
    ],
)
def test_invalid_orcid_formats(invalid_orcid):
    """Test various invalid inputs raise OrcidInvalidFormatError."""
    with pytest.raises(OrcidInvalidFormatError):
        sanitize_orcid(invalid_orcid)


# Edge cases and special scenarios
def test_empty_string():
    """Test empty string input raises exception."""
    with pytest.raises(OrcidInvalidFormatError):
        sanitize_orcid("")


def test_partial_url():
    """Test partial URL format."""
    with pytest.raises(OrcidInvalidFormatError):
        sanitize_orcid("https://orcid.org/")


def test_incorrect_checksum_character():
    """Test invalid character in checksum position."""
    with pytest.raises(OrcidInvalidFormatError):
        sanitize_orcid("0000-0001-2345-678!")  # Invalid character


def test_unicode_input():
    """Test unicode string input."""
    assert sanitize_orcid("0000-0001-2345-6789") == "0000-0001-2345-6789"
