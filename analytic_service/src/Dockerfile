FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
WORKDIR /app/src
COPY analytic_service/src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY tracker_db /app/tracker_db
COPY analytic_service/src/ .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
