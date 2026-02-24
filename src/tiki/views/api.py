import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from tiki.models import DCATOutput, UploadedFile
from tiki.services.pipeline import EnrichmentPipeline

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def enrich(request):
    """Accept a file upload and return DCAT-AP JSON-LD."""
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "No file provided"}, status=400)

    upload = UploadedFile.objects.create(
        file=uploaded_file,
        original_filename=uploaded_file.name,
        file_size=uploaded_file.size,
    )

    try:
        pipeline = EnrichmentPipeline()
        dcat_output = pipeline.run(upload)
        return JsonResponse({
            "id": str(upload.id),
            "status": upload.status,
            "jsonld": dcat_output.jsonld,
            "empty_fields": dcat_output.empty_fields,
        })
    except Exception:
        logger.exception("Enrichment failed for upload %s", upload.id)
        return JsonResponse(
            {"id": str(upload.id), "status": "failed", "error": upload.error_message},
            status=500,
        )


@require_GET
def result(request, upload_id):
    """Retrieve the result for a given upload."""
    try:
        upload = UploadedFile.objects.get(id=upload_id)
    except UploadedFile.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    response = {
        "id": str(upload.id),
        "status": upload.status,
        "original_filename": upload.original_filename,
    }

    if upload.status == UploadedFile.Status.FAILED:
        response["error"] = upload.error_message
    elif upload.status == UploadedFile.Status.COMPLETED:
        try:
            dcat_output = upload.dcat_output
            response["jsonld"] = dcat_output.get_merged_jsonld()
            response["empty_fields"] = dcat_output.empty_fields
            response["is_finalized"] = dcat_output.is_finalized
        except DCATOutput.DoesNotExist:
            response["error"] = "DCAT output not found"

    return JsonResponse(response)


@csrf_exempt
@require_POST
def edit_field(request, upload_id):
    """Update empty fields on a DCAT output."""
    try:
        upload = UploadedFile.objects.get(id=upload_id)
        dcat_output = upload.dcat_output
    except (UploadedFile.DoesNotExist, DCATOutput.DoesNotExist):
        return JsonResponse({"error": "Not found"}, status=404)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    field_name = body.get("field")
    value = body.get("value")

    if not field_name or value is None:
        return JsonResponse({"error": "field and value are required"}, status=400)

    dcat_output.user_edits[field_name] = value

    # Remove from empty_fields if it was there
    if field_name in dcat_output.empty_fields:
        dcat_output.empty_fields.remove(field_name)

    dcat_output.save(update_fields=["user_edits", "empty_fields"])

    return JsonResponse({
        "id": str(upload.id),
        "jsonld": dcat_output.get_merged_jsonld(),
        "empty_fields": dcat_output.empty_fields,
    })


@require_GET
def health(request):
    """Liveness check."""
    return JsonResponse({"status": "ok"})
