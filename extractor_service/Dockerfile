FROM tensorflow/tensorflow:latest-gpu

LABEL authors="BKDDFS"

RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python-is-python3 \
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
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

VOLUME /root/.cache/huggingface

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,video,utility
ENV TF_CPP_MIN_LOG_LEVEL 3

COPY . .

EXPOSE 8100

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]