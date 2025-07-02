# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Install system dependencies for geopandas
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY rwanda_map.py .

# Copy modular structure directories
COPY layouts/ ./layouts/
COPY callbacks/ ./callbacks/

# Copy data directory for geographic maps
COPY data/ ./data/

# Expose port 8050
EXPOSE 8050

# Run the application
CMD ["python", "app.py"]
