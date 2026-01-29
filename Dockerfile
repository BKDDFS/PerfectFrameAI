FROM python:3.13.11-slim-bookworm

LABEL authors="BKDDFS"

# Install uv (fixed version)
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /bin/uv

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    yasm \
    libx264-dev \
    libx265-dev \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libavfilter-dev \
    pkg-config \
    libgl1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

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

# Set ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Set cache for ai model (in user home)
ENV HF_HOME=/home/appuser/.cache/huggingface
VOLUME /home/appuser/.cache/huggingface

# Expose the port
EXPOSE 8100

# Run the application
ENTRYPOINT [ "uvicorn", "perfectframe.app:app", "--host", "0.0.0.0", "--port", "8100" ]
