# Use an explicit, stable slim Python runtime image
FROM python:3.10-slim

# Enforce direct output streaming to prevent log buffering delays
ENV PYTHONUNBUFFERED=1

# Establish working directory context inside the virtualized filesystem
WORKDIR /app

# Install analytical modules and file-parsing extensions directly 
RUN pip install --no-cache-dir \
    pandas==2.2.1 \
    openpyxl==3.1.2 \
    pymongo==4.6.2 \
    kafka-python-ng==2.2.2 \
    python-dotenv==1.0.1

# Move localized execution scripts into the container workspace context
COPY worker.py .

# Boot up the long-running consumer daemon background loop
CMD ["python", "-u", "worker.py"]