# An example using multi-stage image builds to create a final image without uv.
# Taken from https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.6.8 /uv /bin/uv

WORKDIR /app

# uv keeps package info at the root of the workspace
# Make sure you build this at the root context 
COPY uv.lock pyproject.toml .python-version /app/

COPY vendor vendor
COPY packages/ packages/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --package infini-gram-attribution-worker --no-install-workspace

COPY ./attribution_worker ./attribution_worker

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package infini-gram-attribution-worker


# Then, use a final image without uv
FROM python:3.12-slim-bookworm AS base

WORKDIR /app

# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

WORKDIR /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV TRANSFORMERS_NO_ADVISORY_WARNINGS=1

FROM base AS dev

ENV OTEL_SERVICE_NAME=infinigram-api-worker-dev
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://otelcol:4318"
ENV ENV=development

CMD ["saq", "--verbose", "--web", "attribution_worker.worker_settings"]

FROM base AS prod

CMD ["saq", "--web", "attribution_worker.worker_settings", "--verbose"]