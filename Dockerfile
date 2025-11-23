# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for neo-mamba and other packages
# neo-mamba requires leveldb and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libleveldb-dev \
    libssl-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the necessary source code directories
COPY backend/ ./backend/
COPY src/ ./src/
COPY scripts/ ./scripts/

# Expose the port the app runs on
EXPOSE 8000

# Set PYTHONPATH to include the current directory so imports work correctly
ENV PYTHONPATH=/app

# Command to run the application
# We run from the root /app so that imports like 'from backend.database' and 'from src.neo_mcp' work
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
