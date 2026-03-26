# Use a specific Python 3.11 version that supports TensorFlow 2.16
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . .

# Install system dependencies (needed for h5py/tensorflow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We use the root-level requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 10000

# Start command
# We use the 'api.main' path because 'api/' is a folder in the root
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "10000"]
