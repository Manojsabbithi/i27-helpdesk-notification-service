FROM python:3.11-slim

# Prevent Python from writing pyc files & enable logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (needed for mysql + email libs)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     default-libmysqlclient-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better Docker caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set a local fallback database URL for container startup.
# Override this at runtime with -e DATABASE_URL="..." for production.
ENV DATABASE_URL="sqlite:///./notification.db"

# Expose service port (logical, not mandatory)
EXPOSE 8084

# Start FastAPI using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8084"]
