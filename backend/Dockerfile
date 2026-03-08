FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python -c \"from db.database import engine, Base; from db.models import *; Base.metadata.create_all(bind=engine)\" && uvicorn api_main:app --host 0.0.0.0 --port 8000"]
