import pytest

from tiki.models import UploadedFile


@pytest.fixture
def uploaded_file(db, tmp_path):
    """Create an UploadedFile with a real temp file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, Tiki!")

    from django.core.files.uploadedfile import SimpleUploadedFile

    upload = UploadedFile.objects.create(
        file=SimpleUploadedFile("test.txt", b"Hello, Tiki!"),
        original_filename="test.txt",
        file_size=12,
    )
    return upload
