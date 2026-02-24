from django.contrib import admin

from .models import ClaudeEnrichment, DCATOutput, TikaMetadata, UploadedFile


class TikaMetadataInline(admin.StackedInline):
    model = TikaMetadata
    extra = 0
    readonly_fields = ["raw_metadata"]


class ClaudeEnrichmentInline(admin.StackedInline):
    model = ClaudeEnrichment
    extra = 0
    readonly_fields = ["raw_response", "prompt_used"]


class DCATOutputInline(admin.StackedInline):
    model = DCATOutput
    extra = 0
    readonly_fields = ["jsonld"]


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ["original_filename", "status", "file_size", "created_at"]
    list_filter = ["status"]
    search_fields = ["original_filename"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [TikaMetadataInline, ClaudeEnrichmentInline, DCATOutputInline]
