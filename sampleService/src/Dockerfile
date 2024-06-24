FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app/src
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]