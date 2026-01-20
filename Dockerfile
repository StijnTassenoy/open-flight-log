FROM python:3.11-slim

ARG PUID=99
ARG PGID=100
ENV PUID=${PUID}
ENV PGID=${PGID}


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 9966

# Start Uvicorn
CMD ["python", "main.py"]
