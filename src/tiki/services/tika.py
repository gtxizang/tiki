import logging
from dataclasses import dataclass, field
from datetime import datetime

from django.conf import settings
from tika import parser as tika_parser

logger = logging.getLogger(__name__)

# Tika uses many different keys for the same metadata field
AUTHOR_KEYS = ["Author", "dc:creator", "meta:author", "creator", "pdf:docinfo:author"]
TITLE_KEYS = ["title", "dc:title", "meta:title", "pdf:docinfo:title"]
CREATED_DATE_KEYS = ["created", "dcterms:created", "meta:creation-date", "Creation-Date"]
MODIFIED_DATE_KEYS = ["modified", "dcterms:modified", "Last-Modified", "Last-Save-Date"]
LANGUAGE_KEYS = ["language", "dc:language", "Content-Language"]


@dataclass
class TikaResult:
    mime_type: str = ""
    language: str = ""
    author: str = ""
    title: str = ""
    created_date: datetime | None = None
    modified_date: datetime | None = None
    full_text: str = ""
    raw_metadata: dict = field(default_factory=dict)


def _first_match(metadata: dict, keys: list[str]) -> str:
    """Return the first non-empty value from metadata matching any of the given keys."""
    for key in keys:
        value = metadata.get(key, "")
        if value:
            return str(value) if not isinstance(value, str) else value
    return ""


def _parse_date(value: str) -> datetime | None:
    """Best-effort ISO date parsing."""
    if not value:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    logger.warning("Could not parse date: %s", value)
    return None


class TikaService:
    def __init__(self, server_url: str | None = None):
        self.server_url = server_url or settings.TIKA_SERVER_URL

    def extract(self, file_path: str) -> TikaResult:
        """Extract text and metadata from a file using Apache Tika."""
        parsed = tika_parser.from_file(file_path, serverEndpoint=self.server_url)

        metadata = parsed.get("metadata", {}) or {}
        content = parsed.get("content", "") or ""

        return TikaResult(
            mime_type=metadata.get("Content-Type", ""),
            language=_first_match(metadata, LANGUAGE_KEYS),
            author=_first_match(metadata, AUTHOR_KEYS),
            title=_first_match(metadata, TITLE_KEYS),
            created_date=_parse_date(_first_match(metadata, CREATED_DATE_KEYS)),
            modified_date=_parse_date(_first_match(metadata, MODIFIED_DATE_KEYS)),
            full_text=content.strip(),
            raw_metadata=metadata,
        )
