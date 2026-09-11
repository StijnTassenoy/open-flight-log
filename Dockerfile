FROM python:3.11-slim

# Define build args for PUID/PGID (defaults to a non-root uid/gid)
ARG PUID=99
ARG PGID=100

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gosu && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create the non-root user/group used to run the app
RUN groupadd -g "${PGID}" ofl \
    && useradd -u "${PUID}" -g "${PGID}" -m -s /bin/bash ofl \
    && mkdir -p /app/run \
    && chown -R "${PUID}:${PGID}" /app

# Expose port
EXPOSE 9966

# Run as non-root user
USER ${PUID}:${PGID}

# Start Uvicorn
CMD ["python", "main.py"]