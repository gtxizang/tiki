import logging

from django.conf import settings

from tiki.models import ClaudeEnrichment, DCATOutput, TikaMetadata, UploadedFile

from .claude import ClaudeResult, ClaudeService
from .dcat_builder import DCATBuilder
from .tika import TikaService

logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    def __init__(self):
        self.tika_service = TikaService()
        self.dcat_builder = DCATBuilder()
        self._claude_enabled = bool(settings.ANTHROPIC_API_KEY)
        if self._claude_enabled:
            self.claude_service = ClaudeService()

    def run(self, upload: UploadedFile) -> DCATOutput:
        """Run the enrichment pipeline: Tika → (optionally Claude) → DCAT-AP."""
        try:
            # Step 1: Extract with Tika
            upload.mark_extracting()
            tika_result = self.tika_service.extract(upload.file.path)

            TikaMetadata.objects.create(
                upload=upload,
                mime_type=tika_result.mime_type,
                language=tika_result.language,
                author=tika_result.author,
                title=tika_result.title,
                created_date=tika_result.created_date,
                modified_date=tika_result.modified_date,
                full_text=tika_result.full_text,
                raw_metadata=tika_result.raw_metadata,
            )

            # Step 2: Enrich with Claude (if API key configured)
            claude_result = None
            if self._claude_enabled:
                upload.mark_enriching()
                claude_result = self.claude_service.enrich(
                    text=tika_result.full_text,
                    title=tika_result.title,
                    author=tika_result.author,
                    mime_type=tika_result.mime_type,
                    language=tika_result.language,
                )

                ClaudeEnrichment.objects.create(
                    upload=upload,
                    suggested_themes=claude_result.suggested_themes,
                    generated_description=claude_result.generated_description,
                    suggested_keywords=claude_result.suggested_keywords,
                    prompt_used=claude_result.prompt_used,
                    raw_response=claude_result.raw_response,
                    model_used=claude_result.model_used,
                )
            else:
                logger.info("Skipping Claude enrichment (no API key configured)")

            # Step 3: Build DCAT-AP JSON-LD
            dcat_result = self.dcat_builder.build(
                tika_result=tika_result,
                claude_result=claude_result,
                filename=upload.original_filename,
                file_size=upload.file_size,
            )

            dcat_output = DCATOutput.objects.create(
                upload=upload,
                jsonld=dcat_result.jsonld,
                empty_fields=dcat_result.empty_fields,
            )

            upload.mark_completed()
            return dcat_output

        except Exception as e:
            logger.exception("Pipeline failed for upload %s", upload.id)
            upload.mark_failed(e)
            raise
