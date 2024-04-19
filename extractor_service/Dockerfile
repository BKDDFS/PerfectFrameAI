FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

LABEL authors="BKDDFS"

RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python-is-python3 \
    ffmpeg \
    build-essential \
    yasm \
    libx264-dev \
    libx265-dev \
    libnuma-dev \
    libfdk-aac-dev \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libavfilter-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

VOLUME /root/.cache
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,video,utility

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8100

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8100/health || exit 1