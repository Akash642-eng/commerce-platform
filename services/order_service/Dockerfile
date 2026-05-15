FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY services/order_service/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x services/order_service/wait-for-db.sh

EXPOSE 8000

CMD ["sh", "services/order_service/wait-for-db.sh"]