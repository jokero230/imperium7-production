ml-tools/Dockerfile
# ═════════════════════════════════════════════════════════════
# IMPERIUM 7™ — HERMES AGENT DOCKERFILE
# Multi-stage build, production-optimized Python container
# ═════════════════════════════════════════════════════════════

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies in virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────
# RUNTIME STAGE
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

LABEL maintainer="Paweł Deputat <admin@deputatai.com>"
LABEL version="1.0.0"
LABEL description="IMPERIUM 7™ — Hermes Agent (async AI orchestration)"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application
COPY . .

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    WORKERS=4

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Non-root user
RUN useradd -m -u 1000 hermes && chown -R hermes:hermes /app
USER hermes

CMD ["python", "-m", "hermes_agent"]
