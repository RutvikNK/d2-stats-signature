FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code (not just api/, but the full backend/ path)
COPY src/backend ./backend

# Ensure backend/api is recognized as a package
RUN touch backend/__init__.py backend/api/__init__.py

# Set the Python path so backend/ is discoverable
ENV PYTHONPATH="/app"
ENV PATH_TO_MANIFEST="/app/backend/manifest"

# Expose FastAPI default port
EXPOSE 8080

# Run the app
CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
