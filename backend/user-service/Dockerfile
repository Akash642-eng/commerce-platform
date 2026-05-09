FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


COPY . .


RUN chmod +x wait-for-db.sh


EXPOSE 8000


CMD ["./wait-for-db.sh"]