# Build stage
FROM python:3.12-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src/ src/

# Install dependencies
RUN uv pip install --system --no-cache .

# Runtime stage
FROM python:3.12-slim

# Install runtime dependencies and Playwright dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 khora

# Set working directory
WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Copy configuration files
COPY .env.example .env

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DAGSTER_HOME=/app/dagster_home

# Create directories
RUN mkdir -p /app/dagster_home && \
    chown -R khora:khora /app

# Switch to non-root user
USER khora

# Install Playwright browsers
RUN playwright install chromium

# Expose Dagster web UI port
EXPOSE 3000

# Default command
CMD ["dagster", "dev", "-f", "src/khora/pipelines/definitions.py", "-p", "3000"]
