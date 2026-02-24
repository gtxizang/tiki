import copy
import uuid

from django.db import models


class UploadedFile(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        EXTRACTING = "extracting", "Extracting"
        ENRICHING = "enriching", "Enriching"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="uploads/%Y/%m/")
    original_filename = models.CharField(max_length=512)
    file_size = models.PositiveBigIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_filename} ({self.status})"

    def mark_extracting(self):
        self.status = self.Status.EXTRACTING
        self.save(update_fields=["status", "updated_at"])

    def mark_enriching(self):
        self.status = self.Status.ENRICHING
        self.save(update_fields=["status", "updated_at"])

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status", "updated_at"])

    def mark_failed(self, error):
        self.status = self.Status.FAILED
        self.error_message = str(error)
        self.save(update_fields=["status", "error_message", "updated_at"])


class TikaMetadata(models.Model):
    upload = models.OneToOneField(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="tika_metadata",
    )
    mime_type = models.CharField(max_length=255, blank=True, default="")
    language = models.CharField(max_length=50, blank=True, default="")
    author = models.CharField(max_length=512, blank=True, default="")
    title = models.CharField(max_length=1024, blank=True, default="")
    created_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    full_text = models.TextField(blank=True, default="")
    raw_metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Tika metadata for {self.upload.original_filename}"


class ClaudeEnrichment(models.Model):
    upload = models.OneToOneField(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="claude_enrichment",
    )
    suggested_themes = models.JSONField(default=list)
    generated_description = models.TextField(blank=True, default="")
    suggested_keywords = models.JSONField(default=list)
    prompt_used = models.TextField(blank=True, default="")
    raw_response = models.JSONField(default=dict)
    model_used = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"Claude enrichment for {self.upload.original_filename}"


class DCATOutput(models.Model):
    upload = models.OneToOneField(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name="dcat_output",
    )
    jsonld = models.JSONField(default=dict)
    empty_fields = models.JSONField(default=list)
    user_edits = models.JSONField(default=dict)
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"DCAT output for {self.upload.original_filename}"

    def get_merged_jsonld(self):
        """Return JSON-LD with user edits applied."""
        merged = copy.deepcopy(self.jsonld)
        dataset = merged.get("@graph", [{}])[0] if "@graph" in merged else merged
        for field_path, value in self.user_edits.items():
            dataset[field_path] = value
        return merged
