from datetime import datetime

from tiki.services.tika import _first_match, _parse_date


class TestTikaHelpers:
    def test_first_match_found(self):
        metadata = {"dc:creator": "Alice", "Author": "Bob"}
        assert _first_match(metadata, ["Author", "dc:creator"]) == "Bob"

    def test_first_match_fallback(self):
        metadata = {"dc:creator": "Alice"}
        assert _first_match(metadata, ["Author", "dc:creator"]) == "Alice"

    def test_first_match_not_found(self):
        assert _first_match({}, ["Author", "dc:creator"]) == ""

    def test_parse_date_iso(self):
        result = _parse_date("2024-01-15T10:30:00Z")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_parse_date_short(self):
        result = _parse_date("2024-01-15")
        assert isinstance(result, datetime)

    def test_parse_date_empty(self):
        assert _parse_date("") is None

    def test_parse_date_invalid(self):
        assert _parse_date("not-a-date") is None
