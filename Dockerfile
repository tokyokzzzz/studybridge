FROM python:3.12-slim

WORKDIR /app

# System libraries required by psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer is cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Ensure upload and static dirs exist inside the container
RUN mkdir -p /app/media /app/static

EXPOSE 8000

CMD ["python", "entrypoint.py"]
