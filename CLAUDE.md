# Tiki

Django application that accepts file uploads, extracts metadata via Apache Tika, enriches it with Claude (Anthropic API), and returns valid DCAT-AP JSON-LD records.

## Project Layout

- `config/` — Django project settings
- `src/tiki/` — Single Django app with models, services, views
- `tests/` — pytest test suite

## Commands

- `docker compose up` — Run all services (db, tika, web)
- `python manage.py runserver` — Run Django dev server (needs db + tika running)
- `pytest` — Run tests
- `ruff check src/ tests/` — Lint

## Architecture

Single synchronous pipeline: Upload → Tika extraction → Claude enrichment → DCAT-AP JSON-LD output. No Celery. Plain Django views (no DRF).

## Key Paths

- Models: `src/tiki/models/upload.py`
- Services: `src/tiki/services/` (tika, claude, dcat_builder, pipeline)
- Views: `src/tiki/views/` (api.py, ui.py)
