FROM --platform=amd64 python:3.12.4 as base

# Uncomment the following lines to enable GPU support.
# See https://skiff.allenai.org/gpu.html for more details.
#
# ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64
# ENV NVIDIA_VISIBLE_DEVICES all
# ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

FROM base as builder

WORKDIR /api

# Install Python dependencies
COPY requirements requirements
COPY requirements.txt .
COPY vendor vendor
RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt

# Copy over the source code
COPY . .

FROM builder as dev

CMD ["fastapi", "dev", "app.py", "--port", "8000", "--proxy-headers", "--host", "0.0.0.0"]

FROM builder as prod

CMD ["fastapi", "run", "app.py", "--port", "8000", "--proxy-headers", "--workers", "5"]