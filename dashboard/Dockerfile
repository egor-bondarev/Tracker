FROM python:3.11-slim-bookworm
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY scripts/check_tracker.py scripts/check_tracker.py
COPY dashboard/server.py dashboard/server.py
COPY dashboard/static dashboard/static
USER 65534:65534
EXPOSE 8088
CMD ["python", "-m", "dashboard.server"]
