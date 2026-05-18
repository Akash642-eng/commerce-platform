FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# FIX Bug#4: Original had two COPYs:
#   COPY services/api_gateway/ .   <- copies service files into /app
#   COPY . .                       <- overwrites everything with entire repo root!
# The second COPY wiped out the first. We pick ONE approach.
#
# Approach chosen: copy entire repo (matches how shared/ module is needed).
# WORKDIR is /app, repo root lands at /app, so module path is services.api_gateway.app.main
# But api_gateway has no wait-for-db.sh so we call uvicorn directly.

COPY services/api_gateway/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy entire repo so shared/ module is importable as shared.*
COPY . .

CMD ["uvicorn", "services.api_gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
