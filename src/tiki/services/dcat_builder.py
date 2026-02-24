from dataclasses import dataclass, field

from .claude import ClaudeResult
from .tika import TikaResult

DCAT_CONTEXT = {
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

# Required DCAT-AP fields that must be filled by the user if not available
REQUIRED_FIELDS = ["dct:license", "dct:publisher", "dcat:contactPoint"]


@dataclass
class DCATBuildResult:
    jsonld: dict = field(default_factory=dict)
    empty_fields: list[str] = field(default_factory=list)


class DCATBuilder:
    def build(
        self,
        tika_result: TikaResult,
        claude_result: ClaudeResult | None,
        filename: str,
        file_size: int,
    ) -> DCATBuildResult:
        """Assemble a DCAT-AP 2.1.1 JSON-LD record."""
        dataset = {
            "@type": "dcat:Dataset",
            "dct:title": tika_result.title or filename,
            "dct:description": claude_result.generated_description if claude_result else "",
        }

        if claude_result and claude_result.suggested_themes:
            dataset["dcat:theme"] = [
                {"@id": theme} for theme in claude_result.suggested_themes
            ]

        if claude_result and claude_result.suggested_keywords:
            dataset["dcat:keyword"] = claude_result.suggested_keywords

        if tika_result.language:
            dataset["dct:language"] = tika_result.language

        if tika_result.author:
            dataset["dct:creator"] = {
                "@type": "foaf:Agent",
                "foaf:name": tika_result.author,
            }

        if tika_result.created_date:
            dataset["dct:issued"] = {
                "@value": tika_result.created_date.isoformat(),
                "@type": "xsd:dateTime",
            }

        if tika_result.modified_date:
            dataset["dct:modified"] = {
                "@value": tika_result.modified_date.isoformat(),
                "@type": "xsd:dateTime",
            }

        # Placeholders for required fields
        dataset["dct:license"] = ""
        dataset["dct:publisher"] = ""
        dataset["dcat:contactPoint"] = ""

        distribution = {
            "@type": "dcat:Distribution",
            "dcat:mediaType": tika_result.mime_type,
            "dcat:byteSize": file_size,
            "dct:title": filename,
        }
        dataset["dcat:distribution"] = [distribution]

        jsonld = {
            "@context": DCAT_CONTEXT,
            "@graph": [dataset],
        }

        empty_fields = [f for f in REQUIRED_FIELDS if not dataset.get(f)]

        return DCATBuildResult(jsonld=jsonld, empty_fields=empty_fields)
