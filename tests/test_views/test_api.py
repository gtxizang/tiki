import json

import pytest
from django.test import Client

from tiki.models import DCATOutput, UploadedFile


@pytest.mark.django_db
class TestHealthView:
    def test_health(self):
        client = Client()
        response = client.get("/health/")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.django_db
class TestEnrichView:
    def test_no_file(self):
        client = Client()
        response = client.post("/api/enrich/")
        assert response.status_code == 400
        assert response.json()["error"] == "No file provided"


@pytest.mark.django_db
class TestResultView:
    def test_not_found(self):
        client = Client()
        response = client.get("/api/result/00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404

    def test_result_completed(self, uploaded_file):
        uploaded_file.mark_completed()
        DCATOutput.objects.create(
            upload=uploaded_file,
            jsonld={"@graph": [{"dct:title": "Test"}]},
            empty_fields=["dct:license"],
        )

        client = Client()
        response = client.get(f"/api/result/{uploaded_file.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "jsonld" in data

    def test_result_failed(self, uploaded_file):
        uploaded_file.mark_failed("Something broke")

        client = Client()
        response = client.get(f"/api/result/{uploaded_file.id}/")
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Something broke"


@pytest.mark.django_db
class TestEditFieldView:
    def test_edit_field(self, uploaded_file):
        dcat = DCATOutput.objects.create(
            upload=uploaded_file,
            jsonld={"@graph": [{"dct:title": "Test", "dct:license": ""}]},
            empty_fields=["dct:license"],
        )

        client = Client()
        response = client.post(
            f"/api/result/{uploaded_file.id}/edit/",
            data=json.dumps(
                {"field": "dct:license", "value": "https://creativecommons.org/licenses/by/4.0/"}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "dct:license" not in data["empty_fields"]

    def test_edit_field_missing_params(self, uploaded_file):
        DCATOutput.objects.create(upload=uploaded_file, jsonld={})

        client = Client()
        response = client.post(
            f"/api/result/{uploaded_file.id}/edit/",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestHomeView:
    def test_home_page(self):
        client = Client()
        response = client.get("/")
        assert response.status_code == 200
        assert b"Tiki" in response.content
