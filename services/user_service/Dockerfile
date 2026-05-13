FROM commerce-python-base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait-for-db.sh

EXPOSE 8000

CMD ["./wait-for-db.sh"]