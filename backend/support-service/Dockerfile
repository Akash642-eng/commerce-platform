FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y netcat-openbsd
RUN chmod +x wait-for-db.sh

CMD ["./wait-for-db.sh"]