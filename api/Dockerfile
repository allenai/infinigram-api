# An example using multi-stage image builds to create a final image without uv.
# Taken from https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app
COPY vendor vendor

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Then, use a final image without uv
FROM python:3.12-slim-bookworm as base

COPY vendor/llama-2-7b-hf/ vendor/llama-2-7b-hf/
COPY vendor/olmo-7b-hf/ vendor/olmo-7b-hf/
COPY vendor/llama-2_bow_ids.txt vendor/llama-2_bow_ids.txt

# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

FROM base as dev
ENV OTEL_SERVICE_NAME=infinigram-api-dev
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://otelcol:4318"
ENV ENV=development

CMD ["fastapi", "dev", "/app/app.py", "--port", "8000", "--proxy-headers", "--host", "0.0.0.0"]

FROM base as prod
ENV ENV=production

CMD ["fastapi", "run", "/app/app.py", "--port", "8000", "--proxy-headers"]