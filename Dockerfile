# Multi-stage Dockerfile for Crawl4AI MCP Server
# Optimized for size and caching

# Stage 1: Python dependencies
FROM python:3.11-slim AS dependencies

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Stage 2: Install Playwright browsers + system deps
FROM dependencies AS browsers

# Set a shared browser path so browsers are accessible to any user
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers

# Install Playwright chromium and all required system dependencies
RUN python -m playwright install --with-deps chromium

# Stage 3: Final runtime image
FROM browsers AS runtime

# Copy application code
COPY . .

# Create directories for outputs
RUN mkdir -p /app/crawls /app/test_crawls

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app \
    CRAWL4AI_MCP_LOG=INFO \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers

# Default command runs the MCP server
CMD ["python", "-m", "crawler_agent.mcp_server"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import crawler_agent.mcp_server; print('OK')" || exit 1

# Labels for metadata
LABEL maintainer="crawler_agent" \
      description="Crawl4AI MCP Server - Web scraping and crawling tools for AI agents" \
      version="1.0.0"
