from tiki.services.claude import ClaudeResult
from tiki.services.dcat_builder import DCATBuilder
from tiki.services.tika import TikaResult


class TestDCATBuilder:
    def test_build_basic(self):
        tika_result = TikaResult(
            mime_type="application/pdf",
            title="Test Document",
            author="Jane Doe",
            language="en",
            full_text="Some content",
        )
        claude_result = ClaudeResult(
            suggested_themes=[
                "http://publications.europa.eu/resource/authority/data-theme/GOVE"
            ],
            generated_description="A test document about governance.",
            suggested_keywords=["governance", "test"],
        )

        builder = DCATBuilder()
        result = builder.build(tika_result, claude_result, "test.pdf", 1024)

        jsonld = result.jsonld
        assert "@context" in jsonld
        assert "@graph" in jsonld

        dataset = jsonld["@graph"][0]
        assert dataset["@type"] == "dcat:Dataset"
        assert dataset["dct:title"] == "Test Document"
        assert dataset["dct:description"] == "A test document about governance."
        assert dataset["dct:language"] == "en"
        assert len(dataset["dcat:theme"]) == 1
        assert dataset["dcat:keyword"] == ["governance", "test"]

    def test_empty_fields_detected(self):
        tika_result = TikaResult()
        claude_result = ClaudeResult()

        builder = DCATBuilder()
        result = builder.build(tika_result, claude_result, "file.csv", 512)

        assert "dct:license" in result.empty_fields
        assert "dct:publisher" in result.empty_fields
        assert "dcat:contactPoint" in result.empty_fields

    def test_title_falls_back_to_filename(self):
        tika_result = TikaResult(title="")
        claude_result = ClaudeResult()

        builder = DCATBuilder()
        result = builder.build(tika_result, claude_result, "data.csv", 256)

        dataset = result.jsonld["@graph"][0]
        assert dataset["dct:title"] == "data.csv"
