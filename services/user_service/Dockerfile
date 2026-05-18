FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Build context is the repo ROOT (run: docker build -f services/user_service/Dockerfile .)
# so COPY . . copies the entire repo into /app, making shared/ importable as shared.*

COPY services/user_service/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# FIX Bug#4: Copy entire repo so shared/ is available as a Python package
COPY . .

RUN chmod +x services/user_service/wait-for-db.sh

EXPOSE 8000

# FIX Bug#4: Module path matches the copied repo structure
CMD ["sh", "services/user_service/wait-for-db.sh"]
