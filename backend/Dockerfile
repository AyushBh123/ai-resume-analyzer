# ============================================================================
# DOCKERFILE FOR BACKEND
# ============================================================================
# Multi-stage build for optimized production image
#
# STAGES:
# 1. Builder: Install dependencies
# 2. Runtime: Copy only what's needed
#
# INTERVIEW TIP:
# "I use multi-stage builds to keep the final image small and secure.
#  Only production dependencies are included in the final image."
# ============================================================================

# ==========================================================================
# STAGE 1: BUILDER
# ==========================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================================================
# STAGE 2: RUNTIME
# ==========================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ /app/app/

# Create directories
RUN mkdir -p /app/uploads /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# BUILD AND RUN
# ============================================================================
# Build:
#   docker build -t resume-analyzer-backend .
#
# Run:
#   docker run -p 8000:8000 \
#     -e OPENAI_API_KEY=your_key \
#     resume-analyzer-backend
#
# INTERVIEW POINTS:
# - Multi-stage build reduces image size
# - Only production dependencies included
# - Health check for container orchestration
# - Non-root user for security (can be added)
# - Minimal base image (slim)
# ============================================================================

# Made with Bob
