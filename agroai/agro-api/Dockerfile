# Use official Python 3.11 slim image as base.
FROM python:3.11-slim

# Set working directory inside container.
WORKDIR /app

# Copy requirements first for layer caching (changes to code don't invalidate dependency layer).
COPY requirements.txt .

# Install Python dependencies without caching pip packages.
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire application code.
COPY . .

# Expose port 8000 for FastAPI.
EXPOSE 8000

# Run Uvicorn server on startup.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
