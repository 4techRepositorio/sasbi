FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY packages/contracts /deps/packages/contracts
COPY packages/shared /deps/packages/shared
COPY apps/api /deps/apps/api
COPY apps/worker /deps/apps/worker

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e /deps/packages/contracts \
    && pip install --no-cache-dir -e /deps/packages/shared \
    && pip install --no-cache-dir -e /deps/apps/api \
    && pip install --no-cache-dir -e /deps/apps/worker

WORKDIR /deps/apps/worker

ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "fourpro_worker.celery_app", "worker", "--loglevel=info"]
