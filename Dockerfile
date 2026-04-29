FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .

RUN SECRET_KEY=build \
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=build \
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=build \
    uv run python manage.py collectstatic --no-input

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
