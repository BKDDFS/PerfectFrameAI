FROM python:3.13.12-slim-bookworm@sha256:8092ae2ef67061f9db412458dbdce44dbf16748fb3cae5cdbd020f467a9712d0

LABEL authors="BKDDFS"

# Install uv (fixed version)
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /bin/uv

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip uninstall -y pip && \
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
