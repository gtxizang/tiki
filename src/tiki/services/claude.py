import json
import logging
from dataclasses import dataclass, field

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

TEXT_TRUNCATE_LIMIT = 4000

SYSTEM_PROMPT = """\
You are a metadata enrichment assistant. Given document metadata and text, \
produce a JSON object with these keys:
- "themes": a list of EU Data Theme URIs from \
http://publications.europa.eu/resource/authority/data-theme (e.g. \
"http://publications.europa.eu/resource/authority/data-theme/GOVE")
- "description": a concise description of the document suitable for a \
DCAT-AP dataset record (2-4 sentences)
- "keywords": a list of 3-8 relevant keywords as strings

Respond with ONLY valid JSON, no markdown fences or extra text."""


@dataclass
class ClaudeResult:
    suggested_themes: list[str] = field(default_factory=list)
    generated_description: str = ""
    suggested_keywords: list[str] = field(default_factory=list)
    prompt_used: str = ""
    raw_response: dict = field(default_factory=dict)
    model_used: str = ""


class ClaudeService:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.CLAUDE_MODEL
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def enrich(
        self,
        text: str,
        title: str = "",
        author: str = "",
        mime_type: str = "",
        language: str = "",
    ) -> ClaudeResult:
        """Send document metadata to Claude for enrichment."""
        truncated_text = text[:TEXT_TRUNCATE_LIMIT]

        user_prompt = self._build_prompt(
            truncated_text, title, author, mime_type, language
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text
        raw_response = {
            "content": response_text,
            "model": message.model,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            },
        }

        parsed = self._parse_response(response_text)

        return ClaudeResult(
            suggested_themes=parsed.get("themes", []),
            generated_description=parsed.get("description", ""),
            suggested_keywords=parsed.get("keywords", []),
            prompt_used=user_prompt,
            raw_response=raw_response,
            model_used=message.model,
        )

    def _build_prompt(
        self,
        text: str,
        title: str,
        author: str,
        mime_type: str,
        language: str,
    ) -> str:
        parts = ["Analyse this document and produce metadata enrichment.\n"]
        if title:
            parts.append(f"Title: {title}")
        if author:
            parts.append(f"Author: {author}")
        if mime_type:
            parts.append(f"MIME type: {mime_type}")
        if language:
            parts.append(f"Language: {language}")
        parts.append(f"\nDocument text:\n{text}")
        return "\n".join(parts)

    def _parse_response(self, text: str) -> dict:
        """Parse JSON from Claude's response, handling markdown fences."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]  # Remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]  # Remove closing fence
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude response as JSON: %s", text[:200])
            return {}
