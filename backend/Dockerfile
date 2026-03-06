# Backend Dockerfile for Sales Management System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make wait script executable
RUN chmod +x wait-for-db.py

# Expose port
EXPOSE 8000

# Run the application with wait script
CMD ["sh", "-c", "python wait-for-db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
