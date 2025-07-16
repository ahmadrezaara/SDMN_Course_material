# Start from a lightweight Python base image matching your host version
FROM python:3.8-slim

# Set non-interactive environment for pip
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Create and set working directory
WORKDIR /app

# Copy application code
COPY app.py ./

# Expose the status API port
EXPOSE 8000

# Healthcheck to ensure the server is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD curl -f http://localhost:8000/api/v1/status || exit 1

# Launch the server
ENTRYPOINT ["python3", "app.py"]
