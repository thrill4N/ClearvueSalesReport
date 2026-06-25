# Use an explicit, stable slim Python runtime image
FROM python:3.10-slim

# Enforce direct output streaming to prevent log buffering delays
ENV PYTHONUNBUFFERED=1

# Establish working directory context inside the virtualized filesystem
WORKDIR /app

# Install explicit system dependencies required for data extraction tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python modules directly via pip layers
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.28.0 \
    python-multipart==0.0.9 \
    kafka-python-ng==2.2.2 \
    python-dotenv==1.0.1

# Move localized source code scripts into the container workspace context
COPY app.py .

# Expose network ingress parameters for host machine traffic mapping
EXPOSE 8000

# Execute the asynchronous Uvicorn app process loop on container boot
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]