FROM python:3.13.11-slim-bookworm@sha256:97e9392d12279f8c180eb80f0c7c0f3dfe5650f0f2573f7ad770aea58f75ed12

LABEL authors="BKDDFS"

# Install uv (fixed version)
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /bin/uv

# Install static ffmpeg (reduces CVEs from apt packages)
ARG FFMPEG_VERSION=8.0
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    xz-utils \
    ca-certificates \
    libgl1 \
    libglib2.0-0 && \
    FFMPEG_ARCH=$([ "$TARGETARCH" = "arm64" ] && echo "linuxarm64" || echo "linux64") && \
    curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n${FFMPEG_VERSION}-latest-${FFMPEG_ARCH}-gpl-${FFMPEG_VERSION}.tar.xz" \
    | tar -xJ --strip-components=1 -C /usr/local && \
    apt-get purge -y curl xz-utils && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (production only, no dev deps)
RUN uv sync --frozen --no-dev --no-editable

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"

# Copy the source code into the container
COPY perfectframe/ ./perfectframe/

# Create cache directory and set ownership
RUN mkdir -p /home/appuser/.cache/huggingface && \
    chown -R appuser:appuser /app /home/appuser/.cache

# Set cache for ai model (in user home)
ENV HF_HOME=/home/appuser/.cache/huggingface
VOLUME /home/appuser/.cache/huggingface

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8100

# Run the application
ENTRYPOINT [ "uvicorn", "perfectframe.app:app", "--host", "0.0.0.0", "--port", "8100" ]
