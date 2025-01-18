FROM python:3.12-slim

LABEL authors="BKDDFS"

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

# Set cashe for ai model
VOLUME /root/.cache/huggingface

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,video,utility
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV DOCKER_ENV=1

# Copy the source code into the container
COPY . .

# Expose the port
EXPOSE 8100

# Run the application
ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100" ]