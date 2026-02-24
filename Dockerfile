FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=secret,id=github_token \
    sh -lc 'TOKEN="$(cat /run/secrets/github_token)" && \
    git config --global url."https://${TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com/" && \
    pip install --no-cache-dir -r requirements.txt && \
    # scrub token-bearing git config from the layer
    rm -f /root/.gitconfig /root/.config/git/config 2>/dev/null || true'

COPY . .

ENV PYTHONPATH=/app/src

RUN DJANGO_SECRET_KEY=build-only \
    POSTGRES_HOST=localhost \
    python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8106

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8106", "--workers", "2", "--timeout", "120"]
