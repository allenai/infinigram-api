FROM --platform=amd64 python:3.12.4 as base

FROM base as builder

WORKDIR /attribution-worker

# Install Python dependencies
COPY prod-requirements.txt .
COPY vendor vendor
RUN --mount=type=cache,target=/root/.cache pip install -r prod-requirements.txt

COPY . .

FROM builder as runner

CMD ["saq", "src.worker.settings"]