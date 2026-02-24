import pytest

from tiki.models import ClaudeEnrichment, DCATOutput, TikaMetadata, UploadedFile


@pytest.mark.django_db
class TestUploadedFile:
    def test_create(self, uploaded_file):
        assert uploaded_file.status == UploadedFile.Status.PENDING
        assert uploaded_file.original_filename == "test.txt"
        assert uploaded_file.file_size == 12

    def test_mark_extracting(self, uploaded_file):
        uploaded_file.mark_extracting()
        uploaded_file.refresh_from_db()
        assert uploaded_file.status == UploadedFile.Status.EXTRACTING

    def test_mark_enriching(self, uploaded_file):
        uploaded_file.mark_enriching()
        uploaded_file.refresh_from_db()
        assert uploaded_file.status == UploadedFile.Status.ENRICHING

    def test_mark_completed(self, uploaded_file):
        uploaded_file.mark_completed()
        uploaded_file.refresh_from_db()
        assert uploaded_file.status == UploadedFile.Status.COMPLETED

    def test_mark_failed(self, uploaded_file):
        uploaded_file.mark_failed("Something went wrong")
        uploaded_file.refresh_from_db()
        assert uploaded_file.status == UploadedFile.Status.FAILED
        assert uploaded_file.error_message == "Something went wrong"

    def test_str(self, uploaded_file):
        assert str(uploaded_file) == "test.txt (pending)"


@pytest.mark.django_db
class TestDCATOutput:
    def test_get_merged_jsonld(self, uploaded_file):
        dcat = DCATOutput.objects.create(
            upload=uploaded_file,
            jsonld={
                "@graph": [
                    {
                        "@type": "dcat:Dataset",
                        "dct:title": "Test",
                        "dct:license": "",
                    }
                ]
            },
            empty_fields=["dct:license"],
            user_edits={"dct:license": "https://creativecommons.org/licenses/by/4.0/"},
        )
        merged = dcat.get_merged_jsonld()
        dataset = merged["@graph"][0]
        assert dataset["dct:license"] == "https://creativecommons.org/licenses/by/4.0/"

    def test_get_merged_jsonld_no_edits(self, uploaded_file):
        dcat = DCATOutput.objects.create(
            upload=uploaded_file,
            jsonld={"@graph": [{"dct:title": "Test"}]},
        )
        merged = dcat.get_merged_jsonld()
        assert merged["@graph"][0]["dct:title"] == "Test"
