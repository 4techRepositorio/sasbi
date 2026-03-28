FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY packages/contracts /deps/packages/contracts
COPY packages/shared /deps/packages/shared
COPY apps/api /deps/apps/api

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e /deps/packages/contracts \
    && pip install --no-cache-dir -e /deps/packages/shared \
    && pip install --no-cache-dir -e /deps/apps/api \
    && chmod +x /deps/apps/api/docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["/deps/apps/api/docker-entrypoint.sh"]
CMD ["uvicorn", "fourpro_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
