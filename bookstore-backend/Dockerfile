FROM python:3.11-slim

WORKDIR /app
# Install PostgreSQL client tools for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Copy entrypoint scripts
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY wait-for-postgres.sh /app/wait-for-postgres.sh
RUN chmod +x /app/docker-entrypoint.sh /app/wait-for-postgres.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
