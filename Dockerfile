FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY test_app.py .
CMD uvicorn test_app:app --host 0.0.0.0 --port ${PORT:-8080}
