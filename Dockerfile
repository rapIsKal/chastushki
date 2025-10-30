# Use official Python 3.11 slim image
FROM python:3.11-slim

# set working dir
WORKDIR /app

# avoid interactive prompts in apt
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# system deps for building TTS / PyTorch deps, ffmpeg, sndfile, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    ca-certificates \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    libasound2-dev \
    cmake \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Add a non-root user (safer)
RUN useradd -m -s /bin/bash appuser
USER appuser
ENV HOME=/home/appuser

# Copy application files (your bot code) and requirements
COPY --chown=appuser:appuser requirements.txt /app/requirements.txt
COPY --chown=appuser:appuser . /app

# Use pip to install dependencies (upgrade pip/wheel first)
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make a directory for models (mounted or for downloads)
RUN mkdir -p /home/appuser/models
VOLUME ["/home/appuser/models"]

# Expose nothing by default (Telegram bot connects outbound)
# Provide an env var for your bot token
ENV BOT_TOKEN=""

# Default command — change to your entrypoint/script
CMD ["python", "main.py"]
