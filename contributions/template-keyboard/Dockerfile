# SPDX-License-Identifier: MIT
FROM debian:13-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git python3 cmake ninja-build g++ pkg-config \
    libpng-dev libjpeg-dev libfmt-dev libsdl2-dev libfreetype-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
